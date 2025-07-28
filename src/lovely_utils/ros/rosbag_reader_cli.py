# util_ros/cli/rosbag_reader_cli.py
import typer
from typing import List
from .rosbag_reader import RosbagReader

app = typer.Typer(name="rosbag")

@app.command()
def save(
    bag_path: str = typer.Option(..., help="Path to the rosbag"),
    topics: List[str] = typer.Option(..., help="List of topics to extract"),
    save_dir: str = typer.Option("output", help="Directory to save messages"),
):
    """Extract and save messages from a rosbag"""
    reader = RosbagReader(bag_path, topics)
    reader.save_msg(save_dir)

@app.command()
def info(
    bag_path: str = typer.Option(..., help="Path to the rosbag"),
    topics: List[str] = typer.Option(..., help="Topics to inspect"),
):
    """Print info about selected topics (TBD)"""
    reader = RosbagReader(bag_path, topics)
    reader.print_info()
