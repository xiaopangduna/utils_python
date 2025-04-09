import cv2
import numpy as np
from .base import CameraModelBase

class PinholeCameraModel(CameraModelBase):
    def calibrate(self, objpoints, imgpoints, image_size):
        ret, K, D, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, image_size, None, None)
        return ret, K, D

    def undistort(self, image, K, D):
        return cv2.undistort(image, K, D)

    def save_params(self, filepath, K, D):
        fs = cv2.FileStorage(filepath, cv2.FILE_STORAGE_WRITE)
        fs.write("camera_matrix", K)
        fs.write("dist_coeffs", D)
        fs.release()

    def load_params(self, filepath):
        fs = cv2.FileStorage(filepath, cv2.FILE_STORAGE_READ)
        K = fs.getNode("camera_matrix").mat()
        D = fs.getNode("dist_coeffs").mat()
        fs.release()
        return K, D
