import typer

from .generate_board import cli as generate_board_cli

app = typer.Typer(name="calibration")
app.add_typer(generate_board_cli.app, name="generate-board")

