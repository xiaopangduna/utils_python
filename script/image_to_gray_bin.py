#!/usr/bin/env python3
"""
将指定文件夹下的图片读取、缩放、转灰度图，并保存为 BIN 格式。

默认将图片 resize 为 640x640，可通过 --width / --height 调整，或使用 --no-resize 保持原尺寸。
默认输出为 uint8 灰度像素按行优先排列的原始二进制数据（无文件头）。
可选写入 8 字节头：width (uint32) + height (uint32)，小端序。
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

import cv2
import numpy as np

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 640


def iter_image_files(input_dir: Path, recursive: bool) -> list[Path]:
    """收集目录中的图片文件。"""
    pattern = "**/*" if recursive else "*"
    files = [
        path
        for path in input_dir.glob(pattern)
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(files)


def read_grayscale(
    image_path: Path,
    size: tuple[int, int] | None = (DEFAULT_WIDTH, DEFAULT_HEIGHT),
) -> np.ndarray:
    """读取图片，可选 resize，并转为灰度图。"""
    image = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise ValueError(f"无法读取图片: {image_path}")

    if size is not None:
        width, height = size
        image = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)

    if image.ndim == 2:
        gray = image
    elif image.ndim == 3:
        if image.shape[2] == 4:
            gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        raise ValueError(f"不支持的图片维度 {image.ndim}: {image_path}")

    return gray.astype(np.uint8, copy=False)


def save_gray_bin(
    gray: np.ndarray,
    bin_path: Path,
    with_header: bool = False,
) -> None:
    """将灰度图保存为 BIN 文件。"""
    if gray.ndim != 2:
        raise ValueError(f"灰度图必须是二维数组，当前维度: {gray.ndim}")

    height, width = gray.shape
    bin_path.parent.mkdir(parents=True, exist_ok=True)

    with open(bin_path, "wb") as file:
        if with_header:
            file.write(struct.pack("<II", width, height))
        file.write(gray.tobytes())


def convert_image_to_gray_bin(
    image_path: Path,
    bin_path: Path,
    with_header: bool = False,
    size: tuple[int, int] | None = (DEFAULT_WIDTH, DEFAULT_HEIGHT),
) -> bool:
    """转换单张图片为灰度 BIN。"""
    try:
        gray = read_grayscale(image_path, size=size)
        save_gray_bin(gray, bin_path, with_header=with_header)
        print(f"成功: {image_path} -> {bin_path} ({gray.shape[1]}x{gray.shape[0]})")
        return True
    except Exception as exc:
        print(f"失败: {image_path} ({exc})")
        return False


def convert_directory_to_gray_bin(
    input_dir: Path,
    output_dir: Path,
    with_header: bool = False,
    recursive: bool = False,
    size: tuple[int, int] | None = (DEFAULT_WIDTH, DEFAULT_HEIGHT),
) -> int:
    """批量转换目录中的图片。"""
    image_files = iter_image_files(input_dir, recursive=recursive)
    if not image_files:
        print(f"未找到图片文件: {input_dir}")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    success_count = 0

    for image_path in image_files:
        if recursive:
            relative_path = image_path.relative_to(input_dir)
            bin_path = output_dir / relative_path.with_suffix(".bin")
        else:
            bin_path = output_dir / f"{image_path.stem}.bin"

        if convert_image_to_gray_bin(
            image_path, bin_path, with_header=with_header, size=size
        ):
            success_count += 1

    print(f"完成: 成功 {success_count}/{len(image_files)}")
    return success_count


def main() -> int:
    parser = argparse.ArgumentParser(description="将图片转为灰度图并保存为 BIN")
    parser.add_argument("--input", "-i", required=True, help="输入图片文件或目录")
    parser.add_argument("--output", "-o", required=True, help="输出 BIN 文件或目录")
    parser.add_argument(
        "--with-header",
        action="store_true",
        help="在 BIN 前写入 width/height 头（各 uint32，小端序）",
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="递归处理子目录中的图片",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=DEFAULT_WIDTH,
        help=f"输出图像宽度（默认 {DEFAULT_WIDTH}）",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=DEFAULT_HEIGHT,
        help=f"输出图像高度（默认 {DEFAULT_HEIGHT}）",
    )
    parser.add_argument(
        "--no-resize",
        action="store_true",
        help="不缩放，保持原图尺寸",
    )
    args = parser.parse_args()

    if args.no_resize:
        size = None
    else:
        if args.width <= 0 or args.height <= 0:
            print("错误: --width 和 --height 必须为正整数")
            return 1
        size = (args.width, args.height)

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"错误: 输入路径不存在: {input_path}")
        return 1

    if input_path.is_file():
        if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            print(f"错误: 不支持的图片格式: {input_path}")
            return 1

        if output_path.suffix.lower() != ".bin":
            print(f"错误: 单文件模式下输出必须是 .bin: {output_path}")
            return 1

        success = convert_image_to_gray_bin(
            input_path,
            output_path,
            with_header=args.with_header,
            size=size,
        )
        return 0 if success else 1

    if input_path.is_dir():
        if output_path.suffix.lower() == ".bin":
            print("错误: 目录模式下 --output 应为输出目录，而非 .bin 文件")
            return 1

        success_count = convert_directory_to_gray_bin(
            input_path,
            output_path,
            with_header=args.with_header,
            recursive=args.recursive,
            size=size,
        )
        return 0 if success_count > 0 else 1

    print(f"错误: 无效输入路径: {input_path}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
