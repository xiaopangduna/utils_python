from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2
import typer

from .aruco_gridboard import ArUcoGridBoardGenerator
from .charuco_board import CharucoBoardGenerator
from .april_board import AprilBoardGenerator

app = typer.Typer(name="generate-board")
aruco_app = typer.Typer(name="aruco-gridboard")
charuco_app = typer.Typer(name="charuco-board")
april_app = typer.Typer(name="april-board")


def _available_dict_names() -> list[str]:
    return sorted([name for name in dir(cv2.aruco) if name.startswith("DICT_")])


def _parse_dictionary(dictionary: str) -> int:
    """
    Parse dictionary option (e.g. 'DICT_6X6_250') to cv2.aruco DICT_* int.
    """
    if dictionary.isdigit():
        return int(dictionary)
    key = dictionary.strip().upper()
    if not key.startswith("DICT_"):
        key = f"DICT_{key}"
    if not hasattr(cv2.aruco, key):
        supported = ", ".join(_available_dict_names())
        raise typer.BadParameter(f"Unknown dictionary '{dictionary}'. Supported: {supported}")
    return int(getattr(cv2.aruco, key))


@aruco_app.command("save")
def aruco_gridboard_save(
    cols: int = typer.Option(1, "--cols", min=1, help="Number of markers in X direction"),
    rows: int = typer.Option(1, "--rows", min=1, help="Number of markers in Y direction"),
    dictionary: str = typer.Option(
        "DICT_6X6_250",
        "--dictionary",
        help="ArUco dictionary name, e.g. DICT_6X6_250",
        show_default=True,
        case_sensitive=False,
        autocompletion=_available_dict_names,
    ),
    start_id: int = typer.Option(150, "--start-id", min=0, help="Start ArUco id"),
    marker_length_mm: float = typer.Option(
        800, "--marker-length-mm", min=0.01, help="Marker side length (mm)"
    ),
    marker_sep_mm: float = typer.Option(
        200, "--marker-sep-mm", min=0.0, help="Separation between markers (mm)"
    ),
    margin_mm: float = typer.Option(100, "--margin-mm", min=0.0, help="Image margin (mm)"),
    dpi: int = typer.Option(
        127,
        "--dpi",
        min=1,
        help=(
            "DPI used for mm<->px conversion. "
            "Best set as an integer multiple of 25.4 "
            "(e.g. 127≈25.4*5) for precise physical size; "
            "may be auto-reduced if resulting image is too large."
        ),
    ),
    out_dir: Optional[Path] = typer.Option(
        None, "--out-dir", help="Output directory (default: current directory)"
    ),
    output_prefix: Optional[str] = typer.Option(
        None,
        "--output-prefix",
        help="File name prefix (without extension). Default: auto-generated.",
    ),
    print_info: bool = typer.Option(
        True, "--print-info/--no-print-info", help="Print board info after saving"
    ),
):
    """Generate an ArUco GridBoard and save as PNG/PDF."""
    generator = ArUcoGridBoardGenerator(
        markers_x=cols,
        markers_y=rows,
        dictionary=_parse_dictionary(dictionary),
        start_id=start_id,
        marker_length_mm=marker_length_mm,
        marker_sep_mm=marker_sep_mm,
        margin_mm=margin_mm,
        dpi=dpi,
    )
    saved = generator.save(output_prefix=output_prefix, folder=str(out_dir) if out_dir else None)
    typer.secho(f"Saved: {saved}", fg=typer.colors.GREEN)
    if print_info:
        typer.echo(generator.info())


app.add_typer(aruco_app, name="aruco-gridboard")


@charuco_app.command("save")
def charuco_board_save(
    cols: int = typer.Option(4, "--cols", min=1, help="Number of chessboard squares in X direction"),
    rows: int = typer.Option(3, "--rows", min=1, help="Number of chessboard squares in Y direction"),
    dictionary: str = typer.Option(
        "DICT_6X6_250",
        "--dictionary",
        help="ArUco dictionary name, e.g. DICT_6X6_250",
        show_default=True,
        case_sensitive=False,
        autocompletion=_available_dict_names,
    ),
    square_length_mm: float = typer.Option(
        20.0, "--square-length-mm", min=0.01, help="Square side length (mm)"
    ),
    marker_length_mm: float = typer.Option(
        12.0, "--marker-length-mm", min=0.01, help="Inner ArUco marker side length (mm)"
    ),
    dpi: int = typer.Option(
        300,
        "--dpi",
        min=1,
        help=(
            "DPI used for mm<->px conversion. "
            "Best set as an integer multiple of 25.4 "
            "(e.g. 127≈25.4*5, 254≈25.4*10) for precise physical size; "
            "may be auto-reduced if resulting image is too large."
        ),
    ),
    out_dir: Optional[Path] = typer.Option(
        None, "--out-dir", help="Output directory (default: current directory)"
    ),
    output_prefix: Optional[str] = typer.Option(
        None,
        "--output-prefix",
        help="File name prefix (without extension). Default: auto-generated.",
    ),
    print_info: bool = typer.Option(
        True, "--print-info/--no-print-info", help="Print board info after saving"
    ),
):
    """Generate a ChArUco board and save as PNG/PDF."""
    generator = CharucoBoardGenerator(
        cols=cols,
        rows=rows,
        dictionary=_parse_dictionary(dictionary),
        square_length_mm=square_length_mm,
        marker_length_mm=marker_length_mm,
        dpi=dpi,
    )
    saved = generator.save(output_prefix=output_prefix, folder=str(out_dir) if out_dir else None)
    typer.secho(f"Saved: {saved}", fg=typer.colors.GREEN)
    if print_info:
        typer.echo(generator.info())


app.add_typer(charuco_app, name="charuco-board")


@april_app.command("save")
def april_board_save(
    cols: int = typer.Option(6, "--cols", min=1, help="Number of tags in X direction"),
    rows: int = typer.Option(6, "--rows", min=1, help="Number of tags in Y direction"),
    marker_length_mm: float = typer.Option(
        80.0, "--marker-length-mm", min=0.01,
        help="Single AprilTag edge length (mm), same role as ArUco marker_length_mm",
    ),
    marker_sep_mm: float = typer.Option(
        24.0,
        "--marker-sep-mm",
        min=0.0,
        help="Separation between tags (mm), like ArUco marker_sep_mm",
    ),
    dictionary: str = typer.Option(
        "t36h11",
        "--dictionary",
        help="AprilTag family string, e.g. t36h11 (parallel to ArUco dictionary)",
        show_default=True,
    ),
    start_id: int = typer.Option(
        0,
        "--start-id",
        min=0,
        help="First AprilTag id (row-major: start_id + cols*row + col)",
    ),
    rotation: int = typer.Option(
        2,
        "--rotation",
        min=0,
        max=3,
        help="Rotate tag bit matrix by k*90deg (np.rot90 k times)",
        show_default=True,
    ),
    symm_corners: bool = typer.Option(
        True,
        "--symm-corners/--no-symm-corners",
        help="Draw symmetric corner squares to aid subpixel corner detection",
        show_default=True,
    ),
    out_dir: Optional[Path] = typer.Option(
        None, "--out-dir", help="Output directory (default: current directory)"
    ),
    output_prefix: Optional[str] = typer.Option(
        None,
        "--output-prefix",
        help="File name prefix (without extension). Default: auto-generated.",
    ),
    print_info: bool = typer.Option(
        True, "--print-info/--no-print-info", help="Print board info after saving"
    ),
):
    """Generate an AprilTag grid (Aprilgrid) and save as PDF."""
    generator = AprilBoardGenerator(
        markers_x=cols,
        markers_y=rows,
        marker_length_mm=marker_length_mm,
        marker_sep_mm=marker_sep_mm,
        dictionary=dictionary,
        start_id=start_id,
        rotation=rotation,
        symm_corners=symm_corners,
    )
    saved = generator.save(
        output_prefix=output_prefix,
        folder=str(out_dir) if out_dir else None,
    )
    typer.secho(f"Saved: {saved}", fg=typer.colors.GREEN)
    if print_info:
        typer.echo(generator.info())


app.add_typer(april_app, name="april-board")

