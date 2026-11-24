# -*- coding: utf-8 -*-
"""Tools for reading videos and writing image sequences."""

import os
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


class VideoProcessor(object):
    @staticmethod
    def extract_frame_from_video(
        path_video: str,
        path_save: str,
        freq: int = 5,
        prefix: str | None = None,
        on_progress: Callable[[int, int, int], None] | None = None,
    ) -> int:
        """Extract frames from a video file at a fixed frame interval.

        Args:
            path_video: Path of the video file.
            path_save: Directory where extracted frames are saved.
            freq: Save one frame every ``freq`` frames. Defaults to 5.
            prefix: Filename prefix. Defaults to the video file name without its suffix.
            on_progress: Optional callback ``(frames_read, total_frames, saved)``.
                ``total_frames`` is 0 when the container does not report a length.
                Calls are throttled to about 10 Hz, with a final call after the last frame.

        Returns:
            Number of frames written.

        Raises:
            ValueError: ``freq`` is less than 1.
            RuntimeError: The video file cannot be opened or a frame cannot be saved.
        """
        if freq < 1:
            raise ValueError(f"freq must be >= 1, got {freq}")

        frame_prefix = prefix or Path(path_video).stem or Path(path_video).name
        if not os.path.isdir(path_save):
            os.makedirs(path_save)

        cap = cv2.VideoCapture(path_video)
        if not cap.isOpened():
            cap.release()
            raise RuntimeError(f"Failed to open video: {path_video}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if total_frames < 0:
            total_frames = 0

        count = 0
        saved = 0
        last_emit = 0.0

        def emit(force: bool = False) -> None:
            nonlocal last_emit
            if on_progress is None:
                return
            now = time.monotonic()
            if not force and now - last_emit < 0.1:
                return
            on_progress(count, total_frames, saved)
            last_emit = now

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if count % freq == 0:
                    path_img = os.path.join(
                        path_save, "{}_{:0>5d}.jpg".format(frame_prefix, count)
                    )
                    if not cv2.imwrite(path_img, frame):
                        raise RuntimeError(f"Failed to save image: {path_img}")
                    saved += 1
                count += 1
                emit()
        finally:
            emit(force=True)
            cap.release()
        return saved

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
