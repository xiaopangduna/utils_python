# -*- coding: utf-8 -*-
"""Tools for reading videos and writing image sequences."""

import re
import shutil
import subprocess
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import cv2

# Directories are scanned one level deep by suffix. An explicit file is accepted as-is.
VIDEO_SUFFIXES = frozenset(
    {
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
        ".m4v",
        ".webm",
        ".wmv",
        ".flv",
        ".mpeg",
        ".mpg",
    }
)


@dataclass(frozen=True)
class VideoInputs:
    """Videos selected from files and directories, in input order."""

    videos: list[Path]
    empty_directories: list[Path]


def collect_video_files(inputs: list[Path]) -> VideoInputs:
    """Resolve files and one-level directories into a deduplicated video list.

    A file is taken as-is. A directory contributes only regular files in that
    directory whose suffix is in ``VIDEO_SUFFIXES``. The same resolved path
    is kept once, at its first occurrence.

    Raises:
        FileNotFoundError: An input path does not exist, or no video was found.
        ValueError: An input exists but is neither a file nor a directory.
    """
    videos: list[Path] = []
    empty_directories: list[Path] = []
    seen: set[Path] = set()

    def add(path: Path) -> None:
        resolved = path.resolve()
        if resolved in seen:
            return
        seen.add(resolved)
        videos.append(resolved)

    for raw in inputs:
        path = raw.expanduser()
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        if path.is_file():
            add(path)
            continue
        if path.is_dir():
            children = sorted(
                (
                    child
                    for child in path.iterdir()
                    if child.is_file() and child.suffix.lower() in VIDEO_SUFFIXES
                ),
                key=lambda child: child.name,
            )
            if not children:
                empty_directories.append(path)
                continue
            for child in children:
                add(child)
            continue
        raise ValueError(f"Not a file or directory: {path}")

    if not videos:
        raise FileNotFoundError("No video files found")
    return VideoInputs(videos=videos, empty_directories=empty_directories)


@dataclass(frozen=True)
class ExtractResult:
    """Frames written by one video extraction."""

    saved: int
    container_frames: int
    undecodable: int


def allocate_output_dir_names(videos: list[Path]) -> list[str]:
    """Return one output directory name per video.

    The name is the video stem. A later video with the same stem gets
    ``stem_2``, ``stem_3``, and so on.
    """
    used: set[str] = set()
    names: list[str] = []
    for video in videos:
        stem = video.stem or video.name
        name = stem
        index = 2
        while name in used:
            name = f"{stem}_{index}"
            index += 1
        used.add(name)
        names.append(name)
    return names


def _container_frame_count(path_video: str) -> int:
    """Return the container's reported frame count, or 0 when it is absent."""
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=nb_frames",
            "-of",
            "default=nokey=1:nw=1",
            path_video,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    text = completed.stdout.strip()
    if not text or text == "N/A":
        return 0
    try:
        count = int(text)
    except ValueError:
        return 0
    return count if count > 0 else 0


def _start_reader(pipe, sink: list[str]) -> threading.Thread:
    def read() -> None:
        if pipe is None:
            return
        for line in pipe:
            sink.append(line)
        pipe.close()

    thread = threading.Thread(target=read, daemon=True)
    thread.start()
    return thread


def _progress_frame(line: str) -> int | None:
    key, separator, value = line.strip().partition("=")
    if separator != "=" or key != "frame":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _frame_indexes(save_dir: Path, prefix: str) -> list[int]:
    pattern = re.compile(rf"^{re.escape(prefix)}_(\d{{5}})\.jpg$")
    indexes: list[int] = []
    for path in save_dir.iterdir():
        match = pattern.match(path.name)
        if match:
            indexes.append(int(match.group(1)))
    return sorted(indexes)


def _renumber_selected_frames(save_dir: Path, prefix: str, freq: int) -> None:
    """Map ffmpeg's output sequence onto decoded-frame indexes."""
    for index in reversed(_frame_indexes(save_dir, prefix)):
        source = save_dir / f"{prefix}_{index:05d}.jpg"
        target = save_dir / f"{prefix}_{index * freq:05d}.jpg"
        if source != target:
            source.rename(target)


class VideoProcessor(object):
    @staticmethod
    def extract_frame_from_video(
        path_video: str,
        path_save: str,
        freq: int = 5,
        prefix: str | None = None,
        on_progress: Callable[[int, int, int], None] | None = None,
    ) -> ExtractResult:
        """Extract frames from a video file at a fixed frame interval.

        Decoding uses ffmpeg so a corrupt packet is skipped and later frames are
        still written. Frame numbers count successfully decoded frames. With
        ``freq`` of 1, ``undecodable`` is the container frame count minus the
        number of frames written.

        Args:
            path_video: Path of the video file.
            path_save: Directory where extracted frames are saved.
            freq: Save one frame every ``freq`` decoded frames. Defaults to 5.
            prefix: Filename prefix. Defaults to the video file name without its suffix.
            on_progress: Optional callback ``(frames_read, total_frames, saved)``.
                ``total_frames`` is 0 when the container does not report a length.
                Calls are throttled to about 10 Hz, with a final call after ffmpeg exits.

        Returns:
            Saved frame count, container frame count, and undecodable frame count.

        Raises:
            ValueError: ``freq`` is less than 1.
            RuntimeError: ffmpeg is missing, or the video cannot be opened and no frame was written.
        """
        if freq < 1:
            raise ValueError(f"freq must be >= 1, got {freq}")
        if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
            raise RuntimeError("ffmpeg and ffprobe must be installed and on PATH")

        frame_prefix = prefix or Path(path_video).stem or Path(path_video).name
        save_dir = Path(path_save)
        save_dir.mkdir(parents=True, exist_ok=True)
        container_frames = _container_frame_count(path_video)
        pattern = str(save_dir / f"{frame_prefix.replace('%', '%%')}_%05d.jpg")
        command = [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-loglevel",
            "error",
            "-progress",
            "pipe:1",
            "-i",
            path_video,
            "-map",
            "0:v:0",
            "-fps_mode",
            "passthrough",
            "-q:v",
            "2",
            "-start_number",
            "0",
        ]
        if freq > 1:
            command.extend(["-vf", f"select=not(mod(n\\,{freq}))"])
        command.append(pattern)

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stderr_lines: list[str] = []
        stderr_thread = _start_reader(process.stderr, stderr_lines)
        last_emit = 0.0
        try:
            assert process.stdout is not None
            for line in process.stdout:
                saved_now = _progress_frame(line)
                if saved_now is None:
                    continue
                now = time.monotonic()
                if on_progress is not None and now - last_emit >= 0.1:
                    on_progress(saved_now * freq, container_frames, saved_now)
                    last_emit = now
        finally:
            return_code = process.wait()
            stderr_thread.join()

        if freq > 1:
            _renumber_selected_frames(save_dir, frame_prefix, freq)
        saved = len(_frame_indexes(save_dir, frame_prefix))
        if on_progress is not None:
            on_progress(saved * freq, container_frames, saved)
        if return_code != 0 and saved == 0:
            detail = stderr_lines[-1].strip() if stderr_lines else "ffmpeg failed"
            raise RuntimeError(f"Failed to open video: {path_video}: {detail}")

        undecodable = 0
        if freq == 1 and container_frames > saved:
            undecodable = container_frames - saved
        return ExtractResult(
            saved=saved,
            container_frames=container_frames,
            undecodable=undecodable,
        )

    @staticmethod
    def merge_image_to_video(
        dir_image,
        path_video,
        img_size: tuple,
        fourcc=cv2.VideoWriter_fourcc(*"XVID"),
        frame_rate: int = 30,
        fn=lambda x: int(x.stem),
    ):
        """Merge images in a directory into a video.

        Args:
            dir_image: Directory of source images.
            path_video: Output video path.
            img_size: Video size as ``(width, height)``.
            fourcc: OpenCV fourcc code.
            frame_rate: Output frame rate.
            fn: Unused sort key kept for call-site compatibility.
        """
        print("-" * 70)
        print("Start merge image to video")
        out = cv2.VideoWriter(
            str(path_video), fourcc, frame_rate, img_size, True
        )
        count = 0
        path_images = [p for p in dir_image.iterdir()]
        path_images.sort()
        # path_images.sort(key=fn)
        for path_image in path_images:
            img = cv2.imread(str(path_image))
            out.write(img)
        if img.shape[0] != img_size[1] or img.shape[1] != img_size[0]:
            print(
                "Warn : Image sizes are inconsistent: image size {}*{} != video size {}*{}".format(
                    img.shape[1],
                    img.shape[0],
                    img_size[0],
                    img_size[1],
                )
            )
        print(
            "Extract {}/{} frame from {} to {}".format(
                count, len(path_images), dir_image, path_video
            )
        )
        print("End merge image to video")
        print("*" * 70)
