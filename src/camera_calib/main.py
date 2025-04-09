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
    camera_model = PinholeCameraModel()

    dir_img = Path(r"/home/xiaopangdun/project/utils_python/notebooks/calibration_data/opencv_sample_data")

    pattern = ChessboardPattern(dir_img=dir_img, board_size=(7, 6), square_size=None)
    path,in_path = pattern.filter_images()
    ret,obj,poexl = pattern.get_objpoints_and_pixelpoints()
    image_size = pattern.get_image_size()

    calibrator = CameraCalibrator(
        camera_model=camera_model,
        pattern=pattern
    )
    calibrator.run()
    # images = load_images_from_dir('./images/')
    # calibrator.run(images, output_file="output.yaml")

if __name__ == "__main__":
    main()
