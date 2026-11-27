import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn

from .video_processor import (
    ExtractResult,
    VideoProcessor,
    allocate_output_dir_names,
    collect_video_files,
)

app = typer.Typer(name="video")


@app.command("extract-frames")
def extract_frames(
    video: list[Path] = typer.Option(
        ...,
        "--video",
        help="Video file or directory. Repeat to pass more than one. A directory is scanned one level deep.",
    ),
    save_dir: Path = typer.Option(
        ...,
        "--save-dir",
        file_okay=False,
        help="Directory to save extracted frames. Each video is written to its own subdirectory.",
    ),
    freq: int = typer.Option(
        5,
        "--freq",
        min=1,
        help="Save one frame every N frames",
    ),
    prefix: str | None = typer.Option(
        None,
        "--prefix",
        help="Filename prefix for saved frames. Defaults to the video file name.",
    ),
):
    """Extract frames from one or more videos at a fixed frame interval."""
    try:
        collected = collect_video_files(video)
    except (FileNotFoundError, ValueError) as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=1) from exc

    for directory in collected.empty_directories:
        typer.secho(
            f"No video files in {directory}",
            fg=typer.colors.YELLOW,
        )

    names = allocate_output_dir_names(collected.videos)
    total = len(collected.videos)
    failed: list[tuple[Path, str]] = []
    succeeded = 0
    total_saved = 0
    for index, (video_path, dirname) in enumerate(
        zip(collected.videos, names), start=1
    ):
        target = save_dir / dirname
        try:
            result = _extract_with_progress(
                video_path, target, freq, prefix, show_progress=sys.stdout.isatty()
            )
        except (RuntimeError, ValueError) as exc:
            failed.append((video_path, str(exc)))
            typer.secho(
                f"[{index}/{total}] {video_path}: failed: {exc}",
                fg=typer.colors.RED,
            )
            continue
        succeeded += 1
        total_saved += result.saved
        typer.secho(
            _saved_message(index, total, video_path, target, result),
            fg=typer.colors.GREEN,
        )

    typer.echo(
        f"done: {succeeded} succeeded, {len(failed)} failed, {total_saved} frame(s)"
    )
    if failed:
        raise typer.Exit(code=1)


def _saved_message(
    index: int,
    total: int,
    video_path: Path,
    target: Path,
    result: ExtractResult,
) -> str:
    message = (
        f"[{index}/{total}] {video_path}: saved {result.saved} frame(s) to {target}"
    )
    if result.undecodable:
        message += (
            f" (container {result.container_frames}, "
            f"{result.undecodable} not decodable)"
        )
    return message


def _frame_status(frames_read: int, total_frames: int, saved: int) -> str:
    if total_frames > 0:
        return f"{frames_read}/{total_frames} frames, saved {saved}"
    return f"saved {saved}"


def _extract_with_progress(
    video_path: Path,
    target: Path,
    freq: int,
    prefix: str | None,
    show_progress: bool,
) -> ExtractResult:
    """Extract frames, refreshing one progress line on an interactive terminal."""
    if not show_progress:
        return VideoProcessor.extract_frame_from_video(
            str(video_path), str(target), freq, prefix
        )

    progress = Progress(
        TextColumn("  {task.fields[status]}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=Console(file=sys.stdout),
        transient=True,
    )
    with progress:
        task_id = progress.add_task("extract", total=None, status="saved 0")

        def on_progress(frames_read: int, total_frames: int, saved: int) -> None:
            status = _frame_status(frames_read, total_frames, saved)
            if total_frames > 0:
                progress.update(
                    task_id,
                    total=max(total_frames, frames_read),
                    completed=frames_read,
                    status=status,
                )
                return
            progress.update(task_id, completed=frames_read, status=status)

        return VideoProcessor.extract_frame_from_video(
            str(video_path),
            str(target),
            freq,
            prefix,
            on_progress=on_progress,
        )
