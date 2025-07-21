from pathlib import Path
import cv2
import os
from camera_models.pinhole import PinholeCameraModel
from patterns.chessboard import ChessboardPattern
from calibrator import CameraCalibrator

def load_images_from_dir(path):
    image_files = [f for f in os.listdir(path) if f.endswith(('.jpg', '.png'))]
    images = [cv2.imread(os.path.join(path, f)) for f in image_files]
    return images
def main():
    # 针孔相机+棋盘标定板
    dir_img = Path(r"/home/ubuntu/桌面/project/C50A_calibr/dataset/250417_calibr_data")
    pattern = ChessboardPattern(dir_img=dir_img, board_size=(5, 6), square_size=None)
    camera_model = PinholeCameraModel()
    calibrator = CameraCalibrator(
        camera_model=camera_model,
        pattern=pattern
    )
    calibrator.run()

if __name__ == "__main__":
    main()
