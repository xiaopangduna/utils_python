from lovely_utils.camera.detector.chessboard_detector import ChessboardDetector
import pytest
import cv2
import numpy as np

from ..util import *


def test_detection_is_success(generate_chessboards_image):
    """测试成功检测到棋盘格的情况"""
    image_chessboard = generate_chessboards_image
    detector = ChessboardDetector(chessboard_size=(6, 9))
    corners, obj_points, drawn_img = detector.detect(image_chessboard)
    assert corners is not None
    assert obj_points is not None
    assert drawn_img is not None
    assert len(corners) == 6 * 9  # 验证角点数量
    assert len(obj_points) == 6 * 9  # 验证真值点数量
    assert drawn_img.shape == image_chessboard.shape

def test_detection_is_failure(generate_white_image):
    """测试未检测到棋盘格的情况"""
    img_white = generate_white_image
    detector = ChessboardDetector()
    corners, obj_points, drawn_img = detector.detect(img_white)
    
    assert corners is None
    assert obj_points is None
    assert drawn_img is None
