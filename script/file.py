from pathlib import Path
import re
from pathlib import Path
from typing import List, Union, Tuple

from lovely_utils.file.rename import numeric_sort_and_rename_files, batch_rename


def natural_sort_key(path: Path) -> List[Union[int, str]]:
    """
    生成用于自然排序的键，将文件名中的数字部分转换为整数。
    例如：'model (1).safetensors' 排序在 'model (10).safetensors' 之前。
    """
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", path.name)
    ]


def rename_from_txt(
    folder: Union[str, Path],
    txt_file: Union[str, Path],
    suffix: str = ".model",
    allow_overwrite: bool = False,
) -> List[Tuple[Path, Path]]:
    """
    根据 TXT 文件中的名称列表，批量重命名文件夹中的 .safetensors 文件。

    流程：
        1. 读取 TXT 文件（UTF-8 编码），每行一个名称，忽略空行。
        2. 获取文件夹中所有 .safetensors 文件，按自然排序（如 model (1) 在 model (2) 之前）。
        3. 检查文件数量与名称数量是否一致，不一致则报错。
        4. 构造新文件名：名称 + suffix（默认为 .model）。
        5. 调用 batch_rename 执行重命名。

    参数:
        folder: 包含待重命名文件的文件夹路径
        txt_file: 包含新名称列表的文本文件路径（每行一个名称）
        suffix: 新文件的后缀（包含点，如 .model）
        allow_overwrite: 是否允许覆盖已存在的目标文件

    返回:
        List[Tuple[Path, Path]]: 成功重命名的 (旧路径, 新路径) 列表
    """
    folder = Path(folder).resolve()
    txt_file = Path(txt_file).resolve()

    if not folder.is_dir():
        raise NotADirectoryError(f"文件夹不存在: {folder}")
    if not txt_file.is_file():
        raise FileNotFoundError(f"TXT 文件不存在: {txt_file}")

    # 读取名称列表
    with open(txt_file, "r", encoding="utf-8") as f:
        names = [line.strip() for line in f if line.strip()]
    if not names:
        raise ValueError("TXT 文件中没有有效的名称")

    # 获取所有 .safetensors 文件并按自然排序
    safetensors_files = sorted(folder.glob("*.safetensors"), key=natural_sort_key)
    if len(safetensors_files) != len(names):
        raise ValueError(
            f"文件数量 ({len(safetensors_files)}) 与名称数量 ({len(names)}) 不一致！"
        )

    # 构造新文件路径
    old_paths = safetensors_files
    new_paths = [folder / f"{name}{suffix}" for name in names]

    # 执行重命名
    return batch_rename(old_paths, new_paths, allow_overwrite)


if __name__ == "__main__":
    # 功能：按数字排序并重命名图片
    # numeric_sort_and_rename_files(
    #     src_dir=r"C:\path\to\A",
    #     dst_dir=r"C:\path\to\B",
    #     prefix="img_",
    #     key=lambda p: int(p.stem),
    #     num_digits=3,
    #     start_num=1,
    #     copy_files=False,
    # )
    try:
        result = rename_from_txt(
            folder="/home/ubuntu/Desktop/project/2603_审计_模型",  # 当前目录
            txt_file="/home/ubuntu/Desktop/project/names.txt",  # 名称列表文件
            suffix=".model",  # 新后缀
            allow_overwrite=False,  # 不允许覆盖
        )
        print("重命名成功：")
        for old, new in result:
            print(f"{old.name} -> {new.name}")
    except Exception as e:
        print(f"错误: {e}")
