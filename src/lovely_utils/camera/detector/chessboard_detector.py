import cv2
import numpy as np
from .base_detector import BaseDetector


class ChessboardDetector(BaseDetector):
    def __init__(self, 
                 chessboard_size=(7, 6), 
                 square_size=1.0,  # 新增：方格实际尺寸（单位：米/毫米等，根据需求设定）
                 criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001),
                 subpix_window_size=(11, 11),
                 subpix_zero_zone=(-1, -1),
                 color_conversion=cv2.COLOR_BGR2GRAY,
                 text_position=(10, 30),
                 text_font=cv2.FONT_HERSHEY_SIMPLEX,
                 text_scale=1,
                 text_color=(0, 255, 0),
                 text_thickness=2,
                 text_line_type=cv2.LINE_AA):
        """
        棋盘格检测器构造函数
        :param chessboard_size: 棋盘格内角点数量 (行, 列)
        :param square_size: 棋盘格单个方格的物理尺寸（如毫米）
        :param criteria: 亚像素角点检测的终止条件
        ...（其他参数说明不变）
        """
        BaseDetector.__init__(self)
        self.chessboard_size = chessboard_size
        self.square_size = square_size  # 保存方格尺寸
        self.criteria = criteria
        self.subpix_window_size = subpix_window_size
        self.subpix_zero_zone = subpix_zero_zone
        self.color_conversion = color_conversion
        self.text_position = text_position
        self.text_font = text_font
        self.text_scale = text_scale
        self.text_color = text_color
        self.text_thickness = text_thickness
        self.text_line_type = text_line_type
        
    def detect(self, image):
        """
        检测图像中的棋盘格
        :param image: 输入图像 (BGR格式)
        :return: 
            corners: 检测到的角点像素坐标，None表示未检测到
            obj_points: 对应的三维真值点坐标，None表示未检测到
            drawn_image: 绘制了检测结果的图像，None表示未检测到
        """
        # 转换为灰度图
        gray = cv2.cvtColor(image, self.color_conversion)
        
        # 查找棋盘格角点
        ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, None)
        
        if ret:
            # 亚像素级角点精确化
            corners_subpix = cv2.cornerSubPix(
                gray, 
                corners, 
                self.subpix_window_size,  # 使用构造函数传入的搜索窗口大小
                self.subpix_zero_zone,    # 使用构造函数传入的死区大小
                self.criteria
            )
            
            # 生成对应的三维真值点 (假设棋盘格在z=0平面上)
            obj_points = self._generate_object_points()
            
            # 绘制检测结果
            drawn_image = self._draw_chessboard_corners_on_image(image, corners_subpix)
            
            return corners_subpix, obj_points, drawn_image
        else:
            # 未检测到棋盘格
            return None, None, None
    
    def _generate_object_points(self):
        """生成棋盘格对应的三维坐标点（考虑z=0平面，使用实际方格尺寸）"""
        import numpy as np
        # 生成网格坐标并乘以方格尺寸，得到实际物理坐标
        objp = np.zeros((self.chessboard_size[0] * self.chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.chessboard_size[0], 
                              0:self.chessboard_size[1]].T.reshape(-1, 2) * self.square_size
        return objp
    
    def _draw_chessboard_corners_on_image(self, image, corners):
        """在图像上绘制检测到的棋盘格角点"""
        # 创建图像副本，避免修改原图
        drawn_image = image.copy()
        
        # 绘制角点
        cv2.drawChessboardCorners(
            drawn_image, 
            self.chessboard_size, 
            corners, 
            True  # 表示检测成功
        )
        
        # 添加文本信息
        cv2.putText(
            drawn_image, 
            f"Chessboard detected: {self.chessboard_size}",
            self.text_position,       # 使用构造函数传入的文本位置
            self.text_font,           # 使用构造函数传入的字体
            self.text_scale,          # 使用构造函数传入的缩放比例
            self.text_color,          # 使用构造函数传入的颜色
            self.text_thickness,      # 使用构造函数传入的线宽
            self.text_line_type       # 使用构造函数传入的线条类型
        )
        
        return drawn_image
    