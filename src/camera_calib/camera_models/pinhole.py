import cv2
import numpy as np
from .base import CameraModelBase

class PinholeCameraModel(CameraModelBase):
    def calibrate(self, objpoints, imgpoints, image_size):
        ret, K, D, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, image_size, None, None)
        return ret, K, D, rvecs, tvecs

    def undistort(self, img, mtx,  dist,alpha=1):
        h,  w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), alpha, (w,h))
        # undistort
        dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
        # crop the image
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]

        # # undistort
        # mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), 5)
        # dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)
        #  crop the image
        # x, y, w, h = roi
        # dst = dst[y:y+h, x:x+w]
        # cv2.imwrite('calibresult.png', dst)

        return dst

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
