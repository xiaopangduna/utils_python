import cv2
import numpy as np

class PatternBase:
    def __init__(self):
        raise NotImplementedError

    def get_objpoints_and_pixelpoints(self):
        """
        检测标定板上的角点或圆点。
        :param image: 输入图像
        :return: success, objpoints, imgpoints
        """
        raise NotImplementedError

    def get_image_size(self):
        """
        获取图像尺寸
        :param image: 输入图像
        :return: image_size
        """
        raise NotImplementedError