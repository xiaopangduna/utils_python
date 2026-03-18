import os
from typing import Any, Optional, Union

import cv2
import numpy as np
from cv2.aruco import GridBoard, getPredefinedDictionary, DICT_6X6_250
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


class ArUcoGridBoardGenerator:
    """
    生成用于相机标定的 ArUco GridBoard 标定板。

    设计目标：
    - 对外只暴露两个核心方法：`save()` 用于生成并保存 PNG/PDF，`info()` 返回标定板元信息。
    - 初始化即完成棋盘生成，之后多次调用 `save()` 不会重复计算。
    - 保持实现足够精简，但对默认行为（文件名、单位、布局）有清晰约定。

    参数（单位均为毫米，除非特别说明）:
        markers_x: 水平方向上 marker 的个数（列数）。
        markers_y: 垂直方向上 marker 的个数（行数）。
        dictionary: ArUco 字典类型，支持两种形式：
            - 传入 OpenCV 的预定义字典常量（例如 `cv2.aruco.DICT_6X6_250`）
            - 传入 `cv2.aruco.Dictionary` 实例
        start_id: 起始的 ArUco ID，将连续分配 `markers_x * markers_y` 个 ID。
        marker_length_mm: 单个 ArUco 方块的边长。
        marker_sep_mm: 邻近两个 marker 之间的间距（边到边）。
        margin_mm: 整个棋盘图像四周的白边宽度。
        dpi: 生成图像时使用的像素密度，用于在 mm 与像素之间换算。
             为了让 mm 与像素换算无损，推荐设置为 25.4 的整数倍，
             例如 25.4 * 5 ≈ 127、25.4 * 10 ≈ 254。
             当像素尺寸过大时，内部会自动下调 dpi 以避免图像尺寸溢出。

    默认文件命名规则:
        当 `save()` 未显式指定 `output_prefix` 时，会自动使用：

            aruco_gridboard_{cols}x{rows}_id{start}-{end}_L{L}mm

        其中:
            cols / rows: 分别为 `markers_x` / `markers_y`
            start / end: ID 范围 `[start_id, start_id + cols * rows - 1]`
            L: `marker_length_mm`（取整到整数毫米）

    保存位置:
        - 不传 `folder` 时，PNG/PDF 保存在当前工作目录。
        - 传入 `folder` 时，会自动创建目录并将文件保存到该目录下。
    """
    
    def __init__(
        self,
        markers_x: int = 1,
        markers_y: int = 1,
        dictionary: Union[int, Any] = DICT_6X6_250,
        start_id: int = 0,
        marker_length_mm: float = 800,
        marker_sep_mm: float = 200,
        margin_mm: float = 100,
        dpi: int = 127,
    ):
        self.markers_x = markers_x
        self.markers_y = markers_y
        self.dictionary = dictionary
        self.start_id = start_id
        self.marker_length_mm = marker_length_mm
        self.marker_sep_mm = marker_sep_mm
        self.margin_mm = margin_mm
        self.dpi = dpi
        self._dictionary_id: Optional[int] = None

        self._image, self._ids, self._physical_size = self._create_board()

    def _default_prefix(self) -> str:
        """
        根据当前棋盘配置生成默认文件名前缀。

        命名中只编码最关键的几类信息：
        - 棋盘网格尺寸（列 x 行）
        - ID 范围（start-end）
        - marker 实际边长（毫米）
        """
        cols = self.markers_x
        rows = self.markers_y
        start = self.start_id
        end = int(self.start_id + cols * rows - 1)
        length_mm = int(self.marker_length_mm)
        return f"aruco_gridboard_{cols}x{rows}_id{start}-{end}_L{length_mm}mm"
    
    def _mm_to_px(self, mm_value: float, dpi: Optional[int] = None) -> int:
        """将长度从毫米转换为像素，使用给定或实例配置的 dpi。"""
        use_dpi = dpi if dpi is not None else self.dpi
        return round(mm_value / 25.4 * use_dpi)
    
    def _create_board(self):
        """
        创建 ArUco GridBoard 并渲染为灰度图像。

        返回:
            image: 含棋盘与边框的灰度图像（uint8，shape=(H, W)）。
            ids: 使用到的 ArUco ID 数组。
            physical_size: 图像对应的物理尺寸 (width_mm, height_mm)。
        """
        # 单位转换
        dpi = self.dpi
        marker_length_px = self._mm_to_px(self.marker_length_mm, dpi)
        marker_sep_px = self._mm_to_px(self.marker_sep_mm, dpi)
        margin_px = self._mm_to_px(self.margin_mm, dpi)
        
        # 创建字典和ID
        if isinstance(self.dictionary, int):
            self._dictionary_id = int(self.dictionary)
            dictionary = getPredefinedDictionary(self._dictionary_id)
        else:
            self._dictionary_id = None
            dictionary = self.dictionary
        num_markers = self.markers_x * self.markers_y
        ids = np.arange(self.start_id, self.start_id + num_markers, dtype=np.int32)

        # 计算图像尺寸
        board_w = self.markers_x * marker_length_px + (self.markers_x - 1) * marker_sep_px
        board_h = self.markers_y * marker_length_px + (self.markers_y - 1) * marker_sep_px
        img_w = board_w + 2 * margin_px
        img_h = board_h + 2 * margin_px

        # 当像素尺寸过大时，自动下调 dpi，避免生成超大图像
        max_side = max(img_w, img_h)
        max_allowed = 20000  # 像素级保护阈值，足够大但避免极端尺寸
        if max_side > max_allowed:
            scale = max_allowed / max_side
            new_dpi = max(1, int(dpi * scale))
            if new_dpi < dpi:
                print(
                    f"[ArUcoGridBoardGenerator] Warning: image size "
                    f"{img_w}x{img_h}px too large at dpi={dpi}, "
                    f"auto-adjusting dpi to {new_dpi} to avoid overflow. "
                    "Physical size remains approximately unchanged."
                )
                dpi = new_dpi
                self.dpi = dpi
                marker_length_px = self._mm_to_px(self.marker_length_mm, dpi)
                marker_sep_px = self._mm_to_px(self.marker_sep_mm, dpi)
                margin_px = self._mm_to_px(self.margin_mm, dpi)
                board_w = (
                    self.markers_x * marker_length_px
                    + (self.markers_x - 1) * marker_sep_px
                )
                board_h = (
                    self.markers_y * marker_length_px
                    + (self.markers_y - 1) * marker_sep_px
                )
                img_w = board_w + 2 * margin_px
                img_h = board_h + 2 * margin_px

        # 创建GridBoard并生成图像
        board = GridBoard(
            (self.markers_x, self.markers_y),
            marker_length_px,
            marker_sep_px,
            dictionary,
            ids,
        )

        image = np.zeros((img_h, img_w), dtype=np.uint8)
        board.generateImage((img_w, img_h), image, marginSize=margin_px, borderBits=1)

        # 计算物理尺寸
        width_mm = img_w / dpi * 25.4
        height_mm = img_h / dpi * 25.4
        physical_size = (width_mm, height_mm)

        return image, ids, physical_size
    
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

        # 保存PNG
        png_path = f"{base}.png"
        cv2.imwrite(png_path, self._image)
        print(f"PNG saved: {png_path}")
        
        # 保存PDF
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
                - markers_x / markers_y: 棋盘网格尺寸。
                - total_markers: 总的 marker 数量。
                - marker_ids: 实际使用到的 ArUco ID 列表。
                - start_id: 起始 ID。
                - physical_size_mm: 整张图像对应的物理尺寸 (width_mm, height_mm)。
                - image_shape: 生成图像的像素尺寸 (height, width)。
        """
        return {
            "markers_x": self.markers_x,
            "markers_y": self.markers_y,
            "total_markers": self.markers_x * self.markers_y,
            "dictionary_id": self._dictionary_id,
            "marker_ids": self._ids.tolist(),
            "start_id": self.start_id,
            "physical_size_mm": self._physical_size,
            "image_shape": self._image.shape
        }


# 便捷函数（向后兼容）
def generate_aruco_gridboard(output_prefix="aruco_gridboard", folder=None, dictionary=DICT_6X6_250):
    """向后兼容的便捷函数"""
    generator = ArUcoGridBoardGenerator(dictionary=dictionary)
    if output_prefix is None:
        saved_files = generator.save(folder=folder)
    else:
        saved_files = generator.save(output_prefix, folder=folder)
    return {
        "generator": generator,
        "saved_files": saved_files,
        "info": generator.info()
    }


# 直接运行示例
if __name__ == "__main__":
    generator = ArUcoGridBoardGenerator()
    generator.save()
    print("Board info:", generator.info())