import cv2
from cv2 import aruco

# 选择字典
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)

# 创建ChArUco board
board = aruco.CharucoBoard(
    (4, 3),        # 棋盘格数量 (cols, rows)
    0.20,          # squareLength (m)
    0.12,          # markerLength (m)
    aruco_dict
)

# 生成图像
img = board.generateImage((10000, 10000))

# 保存
cv2.imwrite("charuco_board.png", img)