from typing import List, Optional
from pathlib import Path

import typer
from rosbags.typesys import get_typestore

from .rosbag_reader import RosbagReader
from .type import ROS_VERSION_MAPPING

app = typer.Typer(name="rosbag")


# @app.command()
# def save(
#     bag_paths: List[str] = typer.Option(..., help="Paths to the rosbag"),
#     topics: List[str] = typer.Option(..., help="List of topics to extract"),
#     save_dir: Optional[str] = typer.Option(
#         None, help="Directory to save messages (default: same directory as bag file)"
#     ),
# ):
#     """Extract and save messages from rosbag files"""
#     total = len(bag_paths)
#     success_bags = []  # 存储成功处理的bag路径
#     failed_bags = []  # 存储失败处理的bag路径及错误信息

#     for i, bag_path in enumerate(bag_paths, 1):
#         bag_path = Path(bag_path)
#         bag_name = bag_path.name
#         typer.echo(f"[{i}/{total}] 处理: {bag_name}")

#         try:
#             # 尝试初始化 reader 并处理
#             reader = RosbagReader(bag_path, topics)
#             reader.save_msg(save_dir)
#             success_bags.append(bag_path)
#             typer.secho(f"[{i}/{total}] 成功: {bag_name}", fg=typer.colors.GREEN)
#         except Exception as e:
#             # 捕获所有异常，记录失败信息并继续处理下一个
#             failed_bags.append((bag_path, str(e)))  # 存储路径和错误信息
#             typer.secho(
#                 f"[{i}/{total}] 失败: {bag_name} (错误: {str(e)})", fg=typer.colors.RED
#             )
#             continue  # 跳过当前bag，处理下一个

#     # 输出最终统计结果
#     typer.echo("\n" + "=" * 50)
#     typer.secho(f"处理完成: 共 {total} 个bag", fg=typer.colors.BLUE)
#     typer.secho(f"成功: {len(success_bags)} 个", fg=typer.colors.GREEN)
#     typer.secho(f"失败: {len(failed_bags)} 个", fg=typer.colors.RED)

#     # 显示失败的具体路径和错误信息
#     if failed_bags:
#         typer.echo("\n失败的bag路径及原因:")
#         for idx, (path, error) in enumerate(failed_bags, 1):
#             typer.echo(f"{idx}. 路径: {path}")
#             typer.echo(f"   错误: {error}\n")


@app.command()
def save(
    bag_paths: List[str] = typer.Option(None, help="Paths to the rosbag"),
    bag_folders: Optional[List[Path]] = typer.Option(
        None,
        help="Directories to search for rosbag files (only first level, .bag files; support multiple folders separated by space)",
    ),
    topics: List[str] = typer.Option(None, help="List of topics to extract"),
    save_dir: Optional[str] = typer.Option(
        None, help="Directory to save messages (default: same directory as bag file)"
    ),
):
    """Extract and save messages from rosbag files"""
    if not bag_paths and not bag_folders:
        typer.secho(
            "错误：必须提供 --bag-paths 或 --bag-folders（或两者都提供）",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    # 1. 处理 --bag-folder 参数
    folder_bags: List[Path] = []
    if bag_folders:
        for folder in bag_folders:  # 新增循环，遍历每个文件夹
            if not folder.exists():
                typer.secho(
                    f"警告：文件夹不存在，跳过 -> {folder}", fg=typer.colors.YELLOW
                )
                continue
            # 提取当前文件夹下的一级 .bag 文件
            current_bags = [p.resolve() for p in folder.glob("*.bag")]
            folder_bags.extend(current_bags)
            typer.echo(f"从文件夹 {folder} 发现 {len(current_bags)} 个 bag 文件")

    # 2. 合并手动传入的 bag 文件
    manual_bags: List[Path] = []
    if bag_paths:
        manual_bags = [Path(p).resolve() for p in bag_paths]

    # 3. 合并并去重
    all_bags = list(dict.fromkeys(manual_bags + folder_bags))  # 保持顺序去重

    if not all_bags:
        typer.secho("没有找到任何 bag 文件需要处理", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    total = len(all_bags)
    success_bags = []
    failed_bags = []

    for i, bag_path in enumerate(all_bags, 1):
        bag_name = bag_path.name
        typer.echo(f"[{i}/{total}] 处理: {bag_name}")

        try:
            reader = RosbagReader(bag_path, topics)
            reader.save_msg(save_dir)
            success_bags.append(bag_path)
            typer.secho(f"[{i}/{total}] 成功: {bag_name}", fg=typer.colors.GREEN)
        except Exception as e:
            failed_bags.append((bag_path, str(e)))
            typer.secho(
                f"[{i}/{total}] 失败: {bag_name} (错误: {str(e)})", fg=typer.colors.RED
            )
            continue

    typer.echo("\n" + "=" * 50)
    typer.secho(f"处理完成: 共 {total} 个bag", fg=typer.colors.BLUE)
    typer.secho(f"成功: {len(success_bags)} 个", fg=typer.colors.GREEN)
    typer.secho(f"失败: {len(failed_bags)} 个", fg=typer.colors.RED)

    if failed_bags:
        typer.echo("\n失败的bag路径及原因:")
        for idx, (path, error) in enumerate(failed_bags, 1):
            typer.echo(f"{idx}. 路径: {path}")
            typer.echo(f"   错误: {error}\n")


@app.command()
def info(
    bag_paths: List[Path] = typer.Option(
        None,
        help="Paths to one or more rosbag files or directories",
        show_default=True,
    ),
    bag_folders: Optional[List[Path]] = typer.Option(
        None,
        help="Directories to search for rosbag files (only first level, .bag files; support multiple folders)",
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
        typer.echo(
            f"Invalid typestore '{typestore}'. Supported: {', '.join(ROS_VERSION_MAPPING.keys())}"
        )
        raise typer.Exit(code=1)

    ts = get_typestore(ROS_VERSION_MAPPING[typestore])

    # 1. 处理 --bag-folder 参数，扫描一级目录下的 .bag 文件
    folder_bags: List[Path] = []
    if bag_folders:
        for folder in bag_folders:
            if not folder.exists():
                typer.secho(
                    f"警告：文件夹不存在，跳过 -> {folder}", fg=typer.colors.YELLOW
                )
                continue
            # 只扫描一级目录
            found = [p.resolve() for p in folder.glob("*.bag")]
            folder_bags.extend(found)
            typer.echo(f"从文件夹 {folder} 发现 {len(found)} 个 bag 文件")

    # 2. 合并 bag_paths 和 folder_bags，并去重（保持顺序）
    if bag_paths:
        all_bags = list(dict.fromkeys(bag_paths + folder_bags))
    else:
        all_bags = list(dict.fromkeys(folder_bags))
        
    for bag_path in all_bags:
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
