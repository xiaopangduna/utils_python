import os
from typing import Any, Optional, Union

import cv2
import numpy as np
from cv2 import aruco
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


class CharucoBoardGenerator:
    """
    生成用于相机标定的 ChArUco 标定板。

    设计目标与 `ArUcoGridBoardGenerator` 保持一致：
    - 初始化即完成棋盘生成，之后多次调用 `save()` 不会重复计算。
    - 对外只暴露 `save()` / `info()` 两个核心方法。

    参数（单位均为毫米，除非特别说明）:
        cols: 水平方向棋盘格（方块）的个数。
        rows: 垂直方向棋盘格（方块）的个数。
        dictionary: ArUco 字典类型，支持两种形式：
            - 传入 OpenCV 的预定义字典常量（例如 `cv2.aruco.DICT_6X6_250`）
            - 传入 `cv2.aruco.Dictionary` 实例
        square_length_mm: 单个棋盘格边长。
        marker_length_mm: 每个小 ArUco marker 的边长。
        dpi: 生成图像时使用的像素密度，用于在 mm 与像素之间换算。
             为了让 mm 与像素换算无损，推荐设置为 25.4 的整数倍，
             例如 25.4 * 5 ≈ 127、25.4 * 10 ≈ 254。
             当像素尺寸过大时，内部会自动下调 dpi 以避免图像尺寸溢出。

    默认文件命名规则:
        当 `save()` 未显式指定 `output_prefix` 时，会自动使用：

            charuco_board_{cols}x{rows}_Ls{S}mm_Lm{M}mm

        其中:
            S: `square_length_mm`（取整到整数毫米）
            M: `marker_length_mm`（取整到整数毫米）

    保存位置:
        - 不传 `folder` 时，PNG/PDF 保存在当前工作目录。
        - 传入 `folder` 时，会自动创建目录并将文件保存到该目录下。
    """

    def __init__(
        self,
        cols: int = 4,
        rows: int = 3,
        dictionary: Union[int, Any] = aruco.DICT_6X6_250,
        square_length_mm: float = 20.0,
        marker_length_mm: float = 12.0,
        dpi: int = 300,
    ):
        self.cols = cols
        self.rows = rows
        self.dictionary = dictionary
        self.square_length_mm = square_length_mm
        self.marker_length_mm = marker_length_mm
        self.dpi = dpi
        self._dictionary_id: Optional[int] = None

        self._image, self._physical_size = self._create_board()

    def _default_prefix(self) -> str:
        """
        根据当前棋盘配置生成默认文件名前缀。
        """
        cols = self.cols
        rows = self.rows
        square_mm = int(self.square_length_mm)
        marker_mm = int(self.marker_length_mm)
        return f"charuco_board_{cols}x{rows}_Ls{square_mm}mm_Lm{marker_mm}mm"

    def _mm_to_px(self, mm_value: float, dpi: Optional[int] = None) -> int:
        """将长度从毫米转换为像素，使用给定或实例配置的 dpi。"""
        use_dpi = dpi if dpi is not None else self.dpi
        return round(mm_value / 25.4 * use_dpi)

    def _create_board(self):
        """
        创建 ChArUco Board 并渲染为灰度图像。

        返回:
            image: 含棋盘的灰度图像（uint8，shape=(H, W)）。
            physical_size: 图像对应的物理尺寸 (width_mm, height_mm)。
        """
        dpi = self.dpi

        # 物理尺寸（不含额外边距）
        width_mm = self.cols * self.square_length_mm
        height_mm = self.rows * self.square_length_mm

        img_w = self._mm_to_px(width_mm, dpi)
        img_h = self._mm_to_px(height_mm, dpi)

        # 当像素尺寸过大时，自动下调 dpi，避免生成超大图像
        max_side = max(img_w, img_h)
        max_allowed = 20000
        if max_side > max_allowed:
            scale = max_allowed / max_side
            new_dpi = max(1, int(dpi * scale))
            if new_dpi < dpi:
                print(
                    f"[CharucoBoardGenerator] Warning: image size "
                    f"{img_w}x{img_h}px too large at dpi={dpi}, "
                    f"auto-adjusting dpi to {new_dpi} to avoid overflow. "
                    "Physical size remains approximately unchanged."
                )
                dpi = new_dpi
                self.dpi = dpi
                img_w = self._mm_to_px(width_mm, dpi)
                img_h = self._mm_to_px(height_mm, dpi)

        # 创建字典
        if isinstance(self.dictionary, int):
            self._dictionary_id = int(self.dictionary)
            dictionary = aruco.getPredefinedDictionary(self._dictionary_id)
        else:
            self._dictionary_id = None
            dictionary = self.dictionary

        # OpenCV 的 CharucoBoard 参数单位为米
        square_length_m = self.square_length_mm / 1000.0
        marker_length_m = self.marker_length_mm / 1000.0

        board = aruco.CharucoBoard(
            (self.cols, self.rows),
            square_length_m,
            marker_length_m,
            dictionary,
        )

        image = np.zeros((img_h, img_w), dtype=np.uint8)
        board.generateImage((img_w, img_h), image, marginSize=0, borderBits=1)

        physical_size = (width_mm, height_mm)
        return image, physical_size

    def save(self, output_prefix=None, folder=None):
        """
        保存标定板为 PNG 和 PDF 文件。

        参数:
            output_prefix:
                文件名前缀，不含扩展名。
                - 为 None 时使用 `_default_prefix()` 自动生成。
                - 为字符串时按给定前缀命名。
            folder:
                目标保存目录。
                - 为 None 时保存到当前工作目录。
                - 为字符串路径时，目录不存在会自动创建。

        返回:
            一个字典:
                {
                    "png": <PNG 文件路径>,
                    "pdf": <PDF 文件路径或 None>
                }
        """
        if output_prefix is None:
            output_prefix = self._default_prefix()

        if folder is not None:
            os.makedirs(folder, exist_ok=True)
            base = os.path.join(folder, output_prefix)
        else:
            base = output_prefix

        png_path = f"{base}.png"
        cv2.imwrite(png_path, self._image)
        print(f"PNG saved: {png_path}")

        pdf_path = None
        if self._physical_size:
            width_mm, height_mm = self._physical_size
            pdf_path = f"{base}.pdf"
            c = canvas.Canvas(pdf_path, pagesize=(width_mm * mm, height_mm * mm))
            c.drawImage(png_path, 0, 0, width=width_mm * mm, height=height_mm * mm)
            c.save()
            print(f"PDF saved: {pdf_path}")

        return {"png": png_path, "pdf": pdf_path}

    def info(self):
        """
        获取当前标定板的元信息。

        返回:
            dict，包含以下字段:
                - cols / rows: 棋盘网格尺寸。
                - square_length_mm / marker_length_mm: 物理尺寸参数。
                - dictionary_id: 若使用预定义字典，则为对应常量值，否则为 None。
                - physical_size_mm: 整张图像对应的物理尺寸 (width_mm, height_mm)。
                - image_shape: 生成图像的像素尺寸 (height, width)。
        """
        return {
            "cols": self.cols,
            "rows": self.rows,
            "square_length_mm": self.square_length_mm,
            "marker_length_mm": self.marker_length_mm,
            "dictionary_id": self._dictionary_id,
            "physical_size_mm": self._physical_size,
            "image_shape": self._image.shape,
        }


if __name__ == "__main__":
    generator = CharucoBoardGenerator()
    generator.save()
    print("Board info:", generator.info())

