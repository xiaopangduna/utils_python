from pathlib import Path

import cv2
import numpy as np
import pytest
from typer.testing import CliRunner

from lovely_utils.cli import app
from lovely_utils.video.video_processor import VideoProcessor

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
    assert sorted(path.name for path in save_dir.glob("cam_*.jpg")) == [
        "cam_00000.jpg",
        "cam_00001.jpg",
        "cam_00002.jpg",
        "cam_00003.jpg",
    ]
