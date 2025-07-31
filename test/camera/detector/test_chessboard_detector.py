from lovely_utils.camera.detector.chessboard_detector import ChessboardDetector
import pytest
import cv2
import numpy as np


# 全局测试数据准备
@pytest.fixture(scope="module")
def test_images():
    """创建测试用的各种图像"""
    return {
        "chessboard": _create_test_chessboard((640, 480), (10, 8), 50),
        "empty": np.zeros((480, 640, 3), dtype=np.uint8),
        "small": np.zeros((20, 20, 3), dtype=np.uint8),
        "rgb_chessboard": cv2.cvtColor(_create_test_chessboard((640, 480), (10, 8), 50), cv2.COLOR_BGR2RGB),
        "gray_chessboard": cv2.cvtColor(
            _create_test_chessboard((640, 480), (10, 8), 50), 
            cv2.COLOR_BGR2GRAY
        )
    }

def _create_test_chessboard(size, corners, square_size):
    """辅助方法：创建一张包含棋盘格的测试图像"""
    img = np.ones((size[1], size[0], 3), dtype=np.uint8) * 255  # 白色背景
    rows, cols = corners
    
    # 绘制网格线
    for i in range(rows + 1):
        for j in range(cols + 1):
            cv2.line(img, (j * square_size, 0), (j * square_size, size[1]), (0, 0, 0), 1)
            cv2.line(img, (0, i * square_size), (size[0], i * square_size), (0, 0, 0), 1)
    
    # 填充黑白方块
    for i in range(rows):
        for j in range(cols):
            if (i + j) % 2 == 0:
                cv2.rectangle(
                    img,
                    (j * square_size, i * square_size),
                    ((j + 1) * square_size, (i + 1) * square_size),
                    (0, 0, 0),
                    -1
                )
    return img

def test_detection_success(test_images):
    """测试成功检测到棋盘格的情况"""
    chess_board = test_images["chessboard"]
    detector = ChessboardDetector(chessboard_size=(10, 8))
    corners, obj_points, drawn_img = detector.detect(test_images["chessboard"])
    assert corners is not None
    assert obj_points is not None
    assert drawn_img is not None
    assert len(corners) == 10 * 8  # 验证角点数量
    assert len(obj_points) == 10 * 8  # 验证真值点数量
    assert drawn_img.shape == test_images["chessboard"].shape

def test_detection_failure(test_images):
    """测试未检测到棋盘格的情况"""
    detector = ChessboardDetector()
    corners, obj_points, drawn_img = detector.detect(test_images["empty"])
    
    assert corners is None
    assert obj_points is None
    assert drawn_img is None

def test_small_image(test_images):
    """测试过小的图像处理"""
    detector = ChessboardDetector()
    corners, _, _ = detector.detect(test_images["small"])
    assert corners is None

def test_custom_parameters(test_images):
    """测试自定义参数是否生效"""
    custom_params = {
        'chessboard_size': (10, 8),
        'subpix_window_size': (9, 9),
        'text_color': (0, 0, 255),
        'text_position': (50, 50)
    }
    detector = ChessboardDetector(** custom_params)
    
    # 验证参数设置
    assert detector.chessboard_size == custom_params['chessboard_size']
    assert detector.subpix_window_size == custom_params['subpix_window_size']
    assert detector.text_color == custom_params['text_color']
    
    # 验证检测功能
    corners, _, _ = detector.detect(test_images["chessboard"])
    assert corners is not None

@pytest.mark.parametrize("image_key", ["rgb_chessboard", "gray_chessboard"])
def test_different_image_formats(test_images, image_key):
    """测试不同格式的图像输入"""
    detector = ChessboardDetector(chessboard_size=(10, 8))
    image = test_images[image_key]
    
    # 如果是灰度图，转换为3通道以便检测器处理
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
    corners, _, _ = detector.detect(image)
    assert corners is not None

def test_invalid_image_input():
    """测试无效的图像输入"""
    detector = ChessboardDetector()
    
    # 测试非numpy数组输入
    with pytest.raises(Exception):
        detector.detect("not_an_image")
    
    # 测试错误维度的输入
    invalid_array = np.zeros((10, 10))  # 2D数组而不是3D
    with pytest.raises(Exception):
        detector.detect(invalid_array)
