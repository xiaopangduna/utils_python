from abc import ABC, abstractmethod
from typing import Any, Optional
from ..detector.base_detector import BaseDetector


class BaseCalibrator(ABC):
    """相机校准基类，定义内参和外参校准的核心接口"""

    def __init__(self, detector: BaseDetector) -> None:
        self.detector = detector  # 特征检测器（如棋盘格角点检测器）

        # 校准结果存储（子类需实现具体赋值）
        self.intrinsic_matrix: Optional[Any] = None  # 内参矩阵 (3x3)
        self.dist_coeffs: Optional[Any] = None  # 畸变系数
        self.extrinsic_R: Optional[Any] = None  # 外参旋转矩阵 (3x3)
        self.extrinsic_t: Optional[Any] = None  # 外参平移向量 (3x1)

    @abstractmethod
    def calibrate_intrinsic(self, **kwargs):
        """
        校准相机内参（焦距、主点、畸变系数等）
        """
        raise NotImplementedError("子类必须实现 calibrate_intrinsic 方法")

    @abstractmethod
    def apply_intrinsic(self, **kwargs):
        """
        应用内参校准结果对图像进行畸变矫正
        """
        raise NotImplementedError("子类必须实现 apply_intrinsic 方法")

    @abstractmethod
    def validate_intrinsic(self, **kwargs):
        """
        验证内参校准精度（如重投影误差）
        """
        raise NotImplementedError("子类必须实现 validate_intrinsic 方法")

    @abstractmethod
    def calibrate_extrinsic(self, **kwargs):
        """
        校准相机外参（相对于世界坐标系的旋转和平移）
        """
        raise NotImplementedError("子类必须实现 calibrate_extrinsic 方法")

    @abstractmethod
    def apply_extrinsic(self, **kwargs):
        """
        应用外参将点从世界坐标系转换到相机坐标系（或反之）
        """
        raise NotImplementedError("子类必须实现 apply_extrinsic 方法")

    @abstractmethod
    def validate_extrinsic(self, **kwargs):
        """
        验证外参校准精度（如坐标转换误差）
        """
        raise NotImplementedError("子类必须实现 validate_extrinsic 方法")
