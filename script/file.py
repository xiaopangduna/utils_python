from pathlib import Path

from lovely_utils.file.rename import numeric_sort_and_rename_files


if __name__ == "__main__":
    # 功能：按数字排序并重命名图片
    numeric_sort_and_rename_files(
        src_dir=r"C:\path\to\A",
        dst_dir=r"C:\path\to\B",
        prefix="img_",
        key=lambda p: int(p.stem),
        num_digits=3,
        start_num=1,
        copy_files=False,
    )
    



