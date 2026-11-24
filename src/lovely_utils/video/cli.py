from pathlib import Path

import typer

from .video_processor import VideoProcessor

app = typer.Typer(name="video")


@app.command("extract-frames")
def extract_frames(
    video: Path = typer.Option(
        ...,
        "--video",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to the video file",
    ),
    save_dir: Path = typer.Option(
        ...,
        "--save-dir",
        file_okay=False,
        help="Directory to save extracted frames",
    ),
    freq: int = typer.Option(
        5,
        "--freq",
        min=1,
        help="Save one frame every N frames",
    ),
    prefix: str = typer.Option(
        "frame",
        "--prefix",
        help="Filename prefix for saved frames",
    ),
):
    """Extract frames from a video at a fixed frame interval."""
    try:
        saved = VideoProcessor.extract_frame_from_video(
            str(video), str(save_dir), freq, prefix
        )
    except (RuntimeError, ValueError) as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    typer.secho(
        f"Saved {saved} frame(s) to {save_dir}",
        fg=typer.colors.GREEN,
    )
