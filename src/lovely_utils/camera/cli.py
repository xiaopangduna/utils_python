import typer

from .calibration import calibration_cli

app = typer.Typer(name="camera")
app.add_typer(calibration_cli.app, name="calibration")

