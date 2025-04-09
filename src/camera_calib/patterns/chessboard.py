import cv2
import numpy as np
from pathlib import Path
from .base import PatternBase
from typing import Union

class ChessboardPattern(PatternBase):
    def __init__(self, dir_img: Union[str, Path], board_size: tuple[int, int], square_size: float, dir_save: Union[str, Path]=None):
        self.dir_img: Path = Path(dir_img) if isinstance(dir_img, str) else dir_img
        if dir_save is None:
            self.dir_save = self.dir_img / 'calibration_results'
            self.dir_save.mkdir(exist_ok=True)
        self.path_imgs: list[Path] = []
        self.path_invalid_img: list[Path] = []
        self.board_size: tuple[int, int] = board_size  # 棋盘格的尺寸，如 (9, 6)
        self.square_size: float = square_size  # 每个格子的大小，单位为毫米
        self.objpoints: list[np.ndarray] = []  # 3D 点的真实世界坐标
        self.imgpoints: list[np.ndarray] = []  # 2D 点的图像坐标
        self.image_size: tuple[int, int] | None = None

    def get_objpoints_and_pixelpoints(self, win_size=(11,11),zeroZone=(-1,-1)):
        self.filter_images()
        self.path_imgs.sort()
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        objp = np.zeros((self.board_size[0]*self.board_size[1],3), np.float32)
        objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)
        for img_path in self.path_imgs:
            img = cv2.imread(str(img_path))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, self.board_size, None)
            if ret:
                self.objpoints.append(objp)
                corners2 = cv2.cornerSubPix(gray,corners, win_size, zeroZone, criteria)
                self.imgpoints.append(corners2)
                cv2.drawChessboardCorners(img, self.board_size, corners2, ret)
                cv2.imwrite(str(self.dir_save / img_path.name), img)
        if len(self.objpoints) == 0:
            return False, None, None
 
        return True, self.objpoints, self.imgpoints
    

    
    def run(self):

        pass

    def get_image_size(self):
        # 首先检查是否有有效的图像路径
        if not self.path_imgs:
            # 若没有有效图像路径，调用 filter_images 方法获取
            self.filter_images()
        # 若仍然没有有效图像路径，返回 None
        if not self.path_imgs:
            return None
        # 初始化一个变量用于存储图像尺寸
        size = None
        for img_path in self.path_imgs:
            try:
                # 读取当前图像
                img = cv2.imread(str(img_path))
                # 检查图像是否成功读取
                if img is not None:
                    # 获取当前图像的高度和宽度
                    height, width = img.shape[:2]
                    current_size = (width, height)
                    if size is None:
                        # 如果是第一张图像，将其尺寸赋值给 size
                        size = current_size
                    elif current_size != size:
                        # 如果当前图像尺寸与之前的尺寸不一致，抛出异常
                        raise ValueError(f"Image size mismatch: {img_path} has size {current_size}, expected {size}")
            except Exception as e:
                # 若读取图像过程中出现异常，打印错误信息
                print(f"Error reading image {img_path}: {e}")
        # 将一致的图像尺寸赋值给 self.image_size 属性
        self.image_size = size
        # 返回图像尺寸
        return self.image_size
    
    def filter_images(self):
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
        self.path_imgs = []
        self.path_invalid_img = []

        def is_valid_image(file):
            try:
                img = cv2.imread(str(file))
                if img is None:
                    return False
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                ret, _ = cv2.findChessboardCorners(gray, self.board_size, None)
                return ret
            except cv2.error:
                return False

        for file in self.dir_img.iterdir():
            if file.is_file() and file.suffix.lower() in image_extensions:
                if is_valid_image(file):
                    self.path_imgs.append(file)
                else:
                    self.path_invalid_img.append(file)
        # 
        print(f"Valid images: {len(self.path_imgs)}")
        print(f"Invalid images: {len(self.path_invalid_img)}")
        # 打印无效图像的路径
        if self.path_invalid_img:
            print("Invalid images:")
            for img_path in self.path_invalid_img:
                print(img_path)
        return self.path_imgs, self.path_invalid_img

