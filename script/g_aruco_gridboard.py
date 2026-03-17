
import cv2
import numpy as np
from cv2.aruco import GridBoard, getPredefinedDictionary, DICT_6X6_250
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from PIL import Image

# =============================
# 1. 参数（物理尺寸）
# =============================

markers_x = 1
markers_y = 1

start_id = 150   # 起始ID，例如 4 -> 会生成 4,5,6,7

marker_length_mm = 800
marker_sep_mm = 200
margin_mm = 100

dpi = 72  # 72

# =============================
# 2. 单位转换
# =============================

def mm_to_px(mm_value, dpi):
    return round(mm_value / 25.4 * dpi)

marker_length_px = mm_to_px(marker_length_mm, dpi)
marker_sep_px = mm_to_px(marker_sep_mm, dpi)
margin_px = mm_to_px(margin_mm, dpi)

# =============================
# 3. 创建 ArUco Board
# =============================

dictionary = getPredefinedDictionary(DICT_6X6_250)

num_markers = markers_x * markers_y

ids = np.arange(start_id, start_id + num_markers, dtype=np.int32)

board = GridBoard(
    (markers_x, markers_y),
    marker_length_px,
    marker_sep_px,
    dictionary,
    ids
)

print("Marker IDs:", ids)

# =============================
# 4. 计算图像尺寸
# =============================

board_w = markers_x * marker_length_px + (markers_x - 1) * marker_sep_px
board_h = markers_y * marker_length_px + (markers_y - 1) * marker_sep_px

img_w = board_w + 2 * margin_px
img_h = board_h + 2 * margin_px

# =============================
# 5. 生成 PNG
# =============================

img = np.zeros((img_h, img_w), dtype=np.uint8)

board.generateImage(
    (img_w, img_h),
    img,
    marginSize=margin_px,
    borderBits=1
)

png_path = "aruco_gridboard.png"
cv2.imwrite(png_path, img)

print("PNG saved:", png_path)

# =============================
# 6. 生成 PDF（保持真实尺寸）
# =============================

width_mm = img_w / dpi * 25.4
height_mm = img_h / dpi * 25.4

pdf_path = "aruco_gridboard.pdf"

c = canvas.Canvas(pdf_path, pagesize=(width_mm * mm, height_mm * mm))

c.drawImage(
    png_path,
    0,
    0,
    width=width_mm * mm,
    height=height_mm * mm
)

c.save()

print("PDF saved:", pdf_path)

print("Board physical size:")
print(f"{width_mm:.1f} mm x {height_mm:.1f} mm")