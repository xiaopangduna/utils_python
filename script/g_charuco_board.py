import cv2
from cv2 import aruco
from pyx import *
from PIL import Image
# =========================
# ChArUco 参数
# =========================

cols = 4
rows = 3
square_mm = 20
marker_mm = 12

squareLength = square_mm / 1000
markerLength = marker_mm / 1000

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)

board = aruco.CharucoBoard(
    (cols, rows),
    squareLength,
    markerLength,
    aruco_dict
)

# =========================
# 生成 PNG
# =========================

dpi = 300

width_mm = cols * square_mm
height_mm = rows * square_mm

px_width = int(width_mm / 25.4 * dpi)
px_height = int(height_mm / 25.4 * dpi)

img = board.generateImage((px_width, px_height))

png_file = "charuco_board.png"
cv2.imwrite(png_file, img)

img = Image.open(png_file)

# =========================
# 用 PyX 生成 PDF
# =========================

c = canvas.canvas()

c.insert(
    bitmap.bitmap(
        0,
        0,
        img,
        width=width_mm,
        height=height_mm
    )
)

c.writePDFfile("charuco_board——111")