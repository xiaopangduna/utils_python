# util_ros/cli.py
import typer
from .ros import rosbag_reader_cli

app = typer.Typer()
app.add_typer(rosbag_reader_cli.app, name="rosbag")

def main():
    app()

if __name__ == "__main__":
    main()
