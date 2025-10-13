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
