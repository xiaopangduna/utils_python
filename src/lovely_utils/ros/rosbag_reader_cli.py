from typing import List, Optional
from pathlib import Path

import typer
from rosbags.typesys import get_typestore

from .rosbag_reader import RosbagReader
from .type import ROS_VERSION_MAPPING

app = typer.Typer(name="rosbag")


@app.command()
def save(
    bag_paths: List[str] = typer.Option(..., help="Paths to the rosbag"),
    topics: List[str] = typer.Option(..., help="List of topics to extract"),
    save_dir: Optional[str] = typer.Option(
        None, help="Directory to save messages (default: same directory as bag file)"
    ),
):
    """Extract and save messages from rosbag files"""
    total = len(bag_paths)
    success_bags = []  # 存储成功处理的bag路径
    failed_bags = []  # 存储失败处理的bag路径及错误信息

    for i, bag_path in enumerate(bag_paths, 1):
        bag_path = Path(bag_path)
        bag_name = bag_path.name
        typer.echo(f"[{i}/{total}] 处理: {bag_name}")

        try:
            # 尝试初始化 reader 并处理
            reader = RosbagReader(bag_path, topics)
            reader.save_msg(save_dir)
            success_bags.append(bag_path)
            typer.secho(f"[{i}/{total}] 成功: {bag_name}", fg=typer.colors.GREEN)
        except Exception as e:
            # 捕获所有异常，记录失败信息并继续处理下一个
            failed_bags.append((bag_path, str(e)))  # 存储路径和错误信息
            typer.secho(
                f"[{i}/{total}] 失败: {bag_name} (错误: {str(e)})", fg=typer.colors.RED
            )
            continue  # 跳过当前bag，处理下一个

    # 输出最终统计结果
    typer.echo("\n" + "=" * 50)
    typer.secho(f"处理完成: 共 {total} 个bag", fg=typer.colors.BLUE)
    typer.secho(f"成功: {len(success_bags)} 个", fg=typer.colors.GREEN)
    typer.secho(f"失败: {len(failed_bags)} 个", fg=typer.colors.RED)

    # 显示失败的具体路径和错误信息
    if failed_bags:
        typer.echo("\n失败的bag路径及原因:")
        for idx, (path, error) in enumerate(failed_bags, 1):
            typer.echo(f"{idx}. 路径: {path}")
            typer.echo(f"   错误: {error}\n")


@app.command()
def info(
    bag_paths: List[Path] = typer.Option(
        ..., 
        exists=True, 
        file_okay=True, 
        dir_okay=True, 
        readable=True,
        help="Paths to one or more rosbag files or directories",
        show_default=True,
    ),
    typestore: str = typer.Option(
        "ros1_noetic",
        help="Type store to use for message types",
        show_default=True,
        case_sensitive=False,
        autocompletion=lambda: list(ROS_VERSION_MAPPING.keys()),
    ),
):
    """Print info about selected topics in one or more rosbags."""
    if typestore not in ROS_VERSION_MAPPING:
        typer.echo(f"Invalid typestore '{typestore}'. Supported: {', '.join(ROS_VERSION_MAPPING.keys())}")
        raise typer.Exit(code=1)

    ts = get_typestore(ROS_VERSION_MAPPING[typestore])

    for bag_path in bag_paths:
        typer.echo(f"\n--- Rosbag: {bag_path} ---")
        try:
            info = RosbagReader.get_info(bag_path, ts)
        except Exception as e:
            typer.echo(f"Failed to read rosbag info for {bag_path}: {e}")
            continue  # 继续处理下一个 rosbag

        # 如果你有 format_info 函数可以格式化，这里调用
        # formatted_info = format_info(info)
        # typer.echo(formatted_info)

        # 目前先直接打印字典，后续可以换成美化输出
        typer.echo(info)