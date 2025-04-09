
class CameraCalibrator:
    def __init__(self, camera_model, pattern):
        self.camera_model = camera_model
        self.pattern = pattern


    def calibrate(self, image_size):
        ret, K, D = self.camera_model.calibrate(self.objpoints, self.imgpoints, image_size)
        return ret, K, D

    def undistort(self, image, K, D):
        return self.camera_model.undistort(image, K, D)

    def save(self, filepath, K, D):
        self.camera_model.save_params(filepath, K, D)

    def run(self):
        ret,objp,pixelp=self.pattern.get_objpoints_and_pixelpoints()
        image_szie = self.pattern.get_image_size()
        ret, mtx, dist = self.camera_model.calibrate(objp, pixelp, image_szie)
        pass
