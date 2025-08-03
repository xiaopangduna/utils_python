import pytest
import numpy as np
import cv2


@pytest.fixture
def generate_chessboards_image(img_size=(640, 480), inner_corners=(6, 9), square_size=40):
    """
    生成符合OpenCV角点检测要求的棋盘格图像
    特点：黑白交替方格，无额外边框，边缘留白，内角点清晰可辨

    :param img_size: 图像尺寸 (width, height)
    :param inner_corners: 内角点数量 (rows, cols)，如(6,9)表示6行9列内角点
    :param square_size: 单个方格的边长（像素）
    :return: 生成的棋盘格图像（BGR格式，np.uint8）
    """
    width, height = img_size
    rows, cols = inner_corners  # 内角点行数和列数（rows对应垂直方向，cols对应水平方向）

    # 1. 计算棋盘格总尺寸（方格数量 = 内角点数量 + 1）
    grid_rows = rows + 1  # 垂直方向的方格数量
    grid_cols = cols + 1  # 水平方向的方格数量
    chessboard_w = grid_cols * square_size  # 棋盘格总宽度
    chessboard_h = grid_rows * square_size  # 棋盘格总高度

    # 2. 检查图像尺寸是否足够（需容纳棋盘格 + 边缘留白）
    # 边缘留白 = 图像尺寸 - 棋盘格尺寸，至少留10像素避免贴边
    if chessboard_w + 20 > width or chessboard_h + 20 > height:
        raise ValueError(
            f"棋盘格尺寸超出图像范围！需要至少 {(chessboard_w+20)}x{(chessboard_h+20)}, "
            f"当前图像尺寸 {width}x{height}"
        )

    # 3. 创建白色背景（OpenCV默认BGR格式，背景色(255,255,255)为白色）
    img = np.full((height, width, 3), 255, dtype=np.uint8)

    # 4. 计算棋盘格左上角起点（居中放置，边缘自然留白）
    start_x = (width - chessboard_w) // 2
    start_y = (height - chessboard_h) // 2

    # 5. 绘制黑白交替方格（核心逻辑，与OpenCV检测逻辑匹配）
    for i in range(grid_rows):
        for j in range(grid_cols):
            # 黑白交替规则：(i+j)为偶数时填充黑色（与OpenCV示例一致）
            if (i + j) % 2 == 0:
                # 计算方格的左上角和右下角坐标
                x1 = start_x + j * square_size
                y1 = start_y + i * square_size
                x2 = start_x + (j + 1) * square_size
                y2 = start_y + (i + 1) * square_size

                # 填充黑色方格（BGR格式(0,0,0)）
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), -1)

    return img


@pytest.fixture
def generate_white_image(width=640, height=480, channels=3):
    """
    生成一张全白图像

    参数:
        width: 图像宽度（像素）
        height: 图像高度（像素）
        channels: 通道数，3为彩色（BGR），1为灰度图

    返回:
        全白图像的NumPy数组（uint8类型）
    """
    # 生成所有像素值为255的数组（255代表白色）
    if channels == 1:
        # 灰度图（单通道）
        white_img = np.full((height, width), 255, dtype=np.uint8)
    else:
        # 彩色图（BGR三通道）
        white_img = np.full((height, width, 3), 255, dtype=np.uint8)

    return white_img


@pytest.fixture
def generate_pinhole_calibrator_intrinsic_params():
    pinhole_calibrator_intrinsic_params = {
        "K": np.array([[534.15663136, 0.0, 341.71479628], [0.0, 534.25492559, 232.05013999], [0.0, 0.0, 1.0]]),
        "D": np.array([[-2.94269293e-01, 1.23247845e-01, 1.13850492e-03, -1.38021876e-04, 1.02084844e-02]]),
        "dir_calib_images": "sample_data/camera/pinhole_calibrator",
        "dir_save_detect_result": "tmp/pinhole",
    }
    return pinhole_calibrator_intrinsic_params


@pytest.fixture
def generate_pinhole_calibrator_extrinsic_params():
    pinhole_calibrator_extrinsic_params = {
        "K": np.array([[571.0, 0.0, 329.86688232], [0.0, 571.0, 239.08282471], [0.0, 0.0, 1.0]]),
        "D": np.array([0.0, 0.0, 0.0, 0.0, 0.0]),
        "rvec_cw": np.array([[1.49020644], [-1.44384833], [1.00700235]]),
        "tvec_cw": np.array([[-0.00566246], [1.01658313], [-0.17384156]]),
        "image_size": (640, 480),
        "img_points": np.array(
            [
                [270.0, 290.0],
                [507.0, 295.0],
                [607.0, 465.0],
                [224.0, 456.0],
            ],
            dtype=np.float32,
        ),
        "obj_points": np.array(
            [
                [2.50, 0.288, -0.07],
                [2.50, -0.612, -0.07],
                [1.60, -0.612, -0.07],
                [1.60, 0.288, -0.07],
            ],
            dtype=np.float32,
        ),
    }
    return pinhole_calibrator_extrinsic_params


@pytest.fixture
def generate_fisheye_calibrator_intrinsic_params():
    fisheye_calibrator_intrinsic_params = {
        "K": np.array([[534.15663136, 0.0, 341.71479628], [0.0, 534.25492559, 232.05013999], [0.0, 0.0, 1.0]]),
        "D": np.array([[-2.94269293e-01, 1.23247845e-01, 1.13850492e-03, -1.38021876e-04, 1.02084844e-02]]),
        "dir_calib_images": "sample_data/camera/fisheye_calibrator",
        "dir_save_detect_result": "tmp/fisheye",
    }
    return fisheye_calibrator_intrinsic_params
