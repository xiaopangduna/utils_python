#!C:/A_Programme/Miniconda/envs/py310 python
# -*- coding: utf-8 -*-
"""
@File    :   file_processor.py
@Time    :   2024/03/20 22:15:52
@Author  :   xiaopangdun
@Email  :   18675381281@163.com
@Version :   1.0
@Desc    :   None
"""

import shutil
from pathlib import Path
from typing import List, Union, Tuple

def batch_rename(
    old_names: List[Union[str, Path]],
    new_names: List[Union[str, Path]],
    allow_overwrite: bool = False,
) -> List[Tuple[Path, Path]]:
    """
    使用 pathlib 批量重命名文件。

    参数:
        old_names: 旧文件名列表（字符串或 Path 对象）
        new_names: 新文件名列表（字符串或 Path 对象）
        allow_overwrite: 是否允许覆盖已存在的目标文件，默认为 False

    返回:
        List[Tuple[Path, Path]]: 成功重命名的 (旧路径, 新路径) 列表

    抛出:
        ValueError: 如果两个列表长度不一致
        FileNotFoundError: 如果某个旧文件不存在
        FileExistsError: 如果 allow_overwrite=False 且目标文件已存在
        OSError: 重命名过程中的其他错误（如权限不足、跨设备等）
    """
    # 1. 转换为 Path 对象并验证列表长度
    old_paths = [Path(p) for p in old_names]
    new_paths = [Path(p) for p in new_names]

    if len(old_paths) != len(new_paths):
        raise ValueError("旧文件名列表和新文件名列表长度必须相同")

    # 2. 检查所有旧文件是否存在
    for old in old_paths:
        if not old.exists():
            raise FileNotFoundError(f"旧文件不存在: {old}")

    # 3. 检查目标文件是否已存在（如果不允许覆盖）
    if not allow_overwrite:
        for new in new_paths:
            if new.exists():
                raise FileExistsError(f"新文件已存在，且 allow_overwrite=False: {new}")

    # 4. 执行重命名
    results = []
    for old, new in zip(old_paths, new_paths):
        try:
            old.rename(new)
            results.append((old, new))
        except OSError as e:
            # 发生错误时，已重命名的文件不会回滚，抛出异常并附带已成功列表
            raise OSError(f"重命名 {old} -> {new} 失败: {e}") from e

    return results


def numeric_sort_and_rename_files(
    src_dir,
    dst_dir,
    prefix,
    key=None,
    num_digits=5,
    start_num=0,
    copy_files=True,
    verbose=True,
):
    """按指定规则排序文件并重命名，然后移动或复制到目标目录（不递归）。

    遍历源目录中的文件（不进入子目录），按指定的 key 函数排序（如果 key=None，
    则使用默认排序），重命名为 `prefix + 序号 + 原扩展名` 的格式，序号从 start_num 开始，
    并用 0 补齐到 num_digits 位。默认打印每一步的操作信息。

    Args:
        src_dir (str or Path): 源文件夹路径。
        dst_dir (str or Path): 目标文件夹路径。
        prefix (str): 新文件名的前缀。
        key (callable, optional): 排序函数，输入为 Path 对象。
            如果为 None，则使用默认排序（按文件名字典序）。
        num_digits (int): 序号的位数，不足用 0 补齐。
        start_num (int): 起始序号，默认从 1 开始。
        copy_files (bool): 是否复制文件（True=复制，False=移动）。
        verbose (bool): 是否打印详细日志（默认 True）。

    Returns:
        bool: 成功返回 True，失败返回 False。
    """
    try:
        src = Path(src_dir)
        dst = Path(dst_dir)
        dst.mkdir(parents=True, exist_ok=True)

        # 获取源目录中的所有文件（不递归）
        files = [p for p in src.glob("*") if p.is_file()]

        # 如果 key 为 None，则使用默认排序
        if key is None:
            files.sort()
        else:
            files.sort(key=key)

        # 重命名并移动/复制
        for i, file_path in enumerate(files, start=start_num):
            new_name = f"{prefix}{str(i).zfill(num_digits)}{file_path.suffix}"
            new_path = dst / new_name

            action = "复制" if copy_files else "移动"
            if verbose:
                print(f"{action}: {file_path.name} -> {new_name}")

            if copy_files:
                shutil.copy2(file_path, new_path)  # 复制（保留元数据）
            else:
                shutil.move(file_path, new_path)  # 移动

        return True

    except Exception as e:
        print(f"发生错误: {e}")
        return False


if __name__ == "__main__":
    # 默认排序（字典序）
    numeric_sort_and_rename_files(
        src_dir=r"C:\path\to\A",
        dst_dir=r"C:\path\to\B",
        prefix="img_",
        num_digits=3,
        start_num=1,
        copy_files=False,
    )

    # 自定义排序（按文件名中的数字）
    numeric_sort_and_rename_files(
        src_dir=r"C:\path\to\A",
        dst_dir=r"C:\path\to\B",
        prefix="img_",
        key=lambda p: int(p.stem),
        num_digits=3,
        start_num=1,
        copy_files=False,
    )
