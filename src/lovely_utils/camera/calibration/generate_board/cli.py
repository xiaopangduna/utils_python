from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2
import typer

from .aruco_gridboard import ArUcoGridBoardGenerator

app = typer.Typer(name="generate-board")
aruco_app = typer.Typer(name="aruco-gridboard")


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

