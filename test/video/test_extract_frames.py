from pathlib import Path

import cv2
import numpy as np
import pytest
from typer.testing import CliRunner

from lovely_utils.cli import app
from lovely_utils.video.video_processor import (
    VideoProcessor,
    allocate_output_dir_names,
    collect_video_files,
)

runner = CliRunner()


def _write_sample_video(path: Path, frame_count: int = 10) -> None:
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"MJPG"),
        10,
        (32, 24),
    )
    assert writer.isOpened()
    try:
        for index in range(frame_count):
            frame = np.zeros((24, 32, 3), dtype=np.uint8)
            frame[:, :] = (index, 0, 0)
            writer.write(frame)
    finally:
        writer.release()


def test_extract_frame_from_video_saves_every_nth_frame(tmp_path: Path):
    video_path = tmp_path / "sample.avi"
    save_dir = tmp_path / "frames"
    _write_sample_video(video_path, frame_count=10)

    saved = VideoProcessor.extract_frame_from_video(
        str(video_path), str(save_dir), freq=2, prefix="frame"
    )

    names = sorted(path.name for path in save_dir.glob("frame_*.jpg"))
    assert saved == 5
    assert names == [
        "frame_00000.jpg",
        "frame_00002.jpg",
        "frame_00004.jpg",
        "frame_00006.jpg",
        "frame_00008.jpg",
    ]


def test_extract_frame_from_video_reports_progress_without_printing_paths(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    video_path = tmp_path / "clip.avi"
    save_dir = tmp_path / "frames"
    _write_sample_video(video_path, frame_count=4)
    events: list[tuple[int, int, int]] = []

    saved = VideoProcessor.extract_frame_from_video(
        str(video_path),
        str(save_dir),
        freq=2,
        on_progress=lambda read, total, written: events.append((read, total, written)),
    )

    captured = capsys.readouterr()
    assert saved == 2
    assert captured.out == ""
    assert events
    frames_read, total_frames, written = events[-1]
    assert frames_read == 4
    assert total_frames >= 0
    assert written == 2


def test_extract_frame_from_video_defaults_prefix_to_video_stem(tmp_path: Path):
    video_path = tmp_path / "clip.avi"
    save_dir = tmp_path / "frames"
    _write_sample_video(video_path, frame_count=2)

    saved = VideoProcessor.extract_frame_from_video(
        str(video_path), str(save_dir), freq=1
    )

    assert saved == 2
    assert sorted(path.name for path in save_dir.glob("*.jpg")) == [
        "clip_00000.jpg",
        "clip_00001.jpg",
    ]


def test_extract_frame_from_video_rejects_unreadable_file(tmp_path: Path):
    video_path = tmp_path / "missing.avi"
    video_path.write_bytes(b"not a video")

    with pytest.raises(RuntimeError, match="Failed to open video"):
        VideoProcessor.extract_frame_from_video(
            str(video_path), str(tmp_path / "frames")
        )


def test_extract_frames_cli(tmp_path: Path):
    video_path = tmp_path / "sample.avi"
    save_dir = tmp_path / "frames"
    _write_sample_video(video_path, frame_count=4)

    result = runner.invoke(
        app,
        [
            "video",
            "extract-frames",
            "--video",
            str(video_path),
            "--save-dir",
            str(save_dir),
            "--freq",
            "1",
            "--prefix",
            "cam",
        ],
    )

    assert result.exit_code == 0
    assert "Success :save image" not in result.stdout
    assert f"saved 4 frame(s) to {save_dir / 'sample'}" in result.stdout
    assert "done: 1 succeeded, 0 failed, 4 frame(s)" in result.stdout
    output_dir = save_dir / "sample"
    assert sorted(path.name for path in output_dir.glob("cam_*.jpg")) == [
        "cam_00000.jpg",
        "cam_00001.jpg",
        "cam_00002.jpg",
        "cam_00003.jpg",
    ]


def test_collect_video_files_keeps_explicit_file_and_scans_one_level(tmp_path: Path):
    first = tmp_path / "a.mp4"
    folder = tmp_path / "clips"
    nested = folder / "nested"
    folder.mkdir()
    nested.mkdir()
    first.write_bytes(b"a")
    (folder / "b.AVI").write_bytes(b"b")
    (folder / "notes.txt").write_bytes(b"skip")
    (nested / "c.mp4").write_bytes(b"c")
    (folder / "a.mp4").write_bytes(b"duplicate-name")

    collected = collect_video_files([first, folder, first])

    assert collected.empty_directories == []
    assert [path.name for path in collected.videos] == ["a.mp4", "a.mp4", "b.AVI"]
    assert collected.videos[0] == first.resolve()
    assert collected.videos[1] == (folder / "a.mp4").resolve()
    assert collected.videos[2] == (folder / "b.AVI").resolve()


def test_collect_video_files_reports_empty_directory_and_rejects_missing(tmp_path: Path):
    empty = tmp_path / "empty"
    empty.mkdir()
    video = tmp_path / "only.mp4"
    video.write_bytes(b"v")

    collected = collect_video_files([empty, video])
    assert collected.videos == [video.resolve()]
    assert collected.empty_directories == [empty]

    with pytest.raises(FileNotFoundError, match="does not exist"):
        collect_video_files([tmp_path / "missing.mp4"])

    with pytest.raises(FileNotFoundError, match="No video files found"):
        collect_video_files([empty])


def test_allocate_output_dir_names_disambiguates_same_stem(tmp_path: Path):
    names = allocate_output_dir_names(
        [
            tmp_path / "cam.mp4",
            tmp_path / "other" / "cam.mov",
            tmp_path / "cam.avi",
        ]
    )
    assert names == ["cam", "cam_2", "cam_3"]


def test_extract_frames_cli_handles_file_and_directory(tmp_path: Path):
    loose = tmp_path / "loose.avi"
    folder = tmp_path / "clips"
    folder.mkdir()
    inside = folder / "inside.avi"
    (folder / "skip.txt").write_text("not a video")
    nested = folder / "nested"
    nested.mkdir()
    (nested / "deep.avi").write_bytes(b"ignored")
    _write_sample_video(loose, frame_count=2)
    _write_sample_video(inside, frame_count=2)
    save_dir = tmp_path / "frames"

    result = runner.invoke(
        app,
        [
            "video",
            "extract-frames",
            "--video",
            str(loose),
            "--video",
            str(folder),
            "--save-dir",
            str(save_dir),
            "--freq",
            "1",
        ],
    )

    assert result.exit_code == 0
    assert "done: 2 succeeded, 0 failed, 4 frame(s)" in result.stdout
    assert "Success :save image" not in result.stdout
    assert sorted(path.name for path in (save_dir / "loose").glob("*.jpg")) == [
        "loose_00000.jpg",
        "loose_00001.jpg",
    ]
    assert sorted(path.name for path in (save_dir / "inside").glob("*.jpg")) == [
        "inside_00000.jpg",
        "inside_00001.jpg",
    ]
    assert not (save_dir / "deep").exists()


def test_extract_frames_cli_continues_after_unreadable_video(tmp_path: Path):
    bad = tmp_path / "bad.avi"
    good = tmp_path / "good.avi"
    bad.write_bytes(b"not a video")
    _write_sample_video(good, frame_count=2)
    save_dir = tmp_path / "frames"

    result = runner.invoke(
        app,
        [
            "video",
            "extract-frames",
            "--video",
            str(bad),
            "--video",
            str(good),
            "--save-dir",
            str(save_dir),
            "--freq",
            "1",
        ],
    )

    assert result.exit_code == 1
    assert f"failed: Failed to open video: {bad}" in result.stdout
    assert "done: 1 succeeded, 1 failed, 2 frame(s)" in result.stdout
    assert sorted(path.name for path in (save_dir / "good").glob("*.jpg")) == [
        "good_00000.jpg",
        "good_00001.jpg",
    ]
