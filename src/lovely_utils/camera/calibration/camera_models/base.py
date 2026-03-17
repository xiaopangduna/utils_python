class CameraModelBase:
    def calibrate(self, objpoints, imgpoints, image_size):
        raise NotImplementedError

    def undistort(self, image, camera_matrix, dist_coeffs):
        raise NotImplementedError

    def save_params(self, filepath, camera_matrix, dist_coeffs):
        raise NotImplementedError

    def load_params(self, filepath):
        raise NotImplementedError
