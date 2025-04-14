import cv2
from camera_models.base import CameraModelBase
from patterns.base import PatternBase

class CameraCalibrator:
    def __init__(self, camera_model, pattern):
        self.camera_model:CameraModelBase = camera_model
        self.pattern: PatternBase= pattern
        self.path_imgs = pattern.path_imgs
        self.dir_save =  pattern.dir_save


    def calibrate(self, image_size):
        ret, K, D = self.camera_model.calibrate(self.objpoints, self.imgpoints, image_size)
        return ret, K, D

    def undistort(self, *args, **kwargs):
        return self.camera_model.undistort(*args, **kwargs)

    def calculate_reprojection_error(self,objpoints, imgpoints, rvecs, tvecs, mtx, dist):
        mean_error = 0
        for i in range(len(objpoints)):
            imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
            error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
            mean_error += error
        print( "total error: {}".format(mean_error/len(objpoints)) )
        return mean_error/len(objpoints)

    def save(self, filepath, K, D):
        self.camera_model.save_params(filepath, K, D)

    def run(self):
        ret,objp,pixelp=self.pattern.get_objpoints_and_pixelpoints()
        image_szie = self.pattern.get_image_size()
        ret, mtx, dist,rvecs, tvecs = self.camera_model.calibrate(objp, pixelp, image_szie)
        # 统计重投影误差
        mean_error = self.calculate_reprojection_error(objp, pixelp, rvecs, tvecs ,mtx, dist)
        # 生成标定结果
        # self.save("calibration_data/calibration_result.yml", mtx, dist)
        # 在一张图片上去畸变
        img = cv2.imread(str(self.pattern.path_imgs[0]))
        img_undistorted = self.undistort(img, mtx, dist, alpha=1)

        cv2.imwrite("orignal.jpg", img)
        cv2.imwrite("undistorted.jpg", img_undistorted)


        pass
