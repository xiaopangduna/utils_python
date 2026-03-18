import typer
from .ros import rosbag_reader_cli
from .camera import cli as camera_cli

app = typer.Typer()
app.add_typer(rosbag_reader_cli.app, name="rosbag")
app.add_typer(camera_cli.app, name="camera")

def main():
    app()

if __name__ == "__main__":
    main()
