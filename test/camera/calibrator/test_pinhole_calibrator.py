from pathlib import Path
from ..util import *
from lovely_utils.camera.calibrator.pinhole_calibrator import PinholeCalibrator
from lovely_utils.camera.detector.chessboard_detector import ChessboardDetector


def test_chessboard_calibrate_intrinsic(generate_pinhole_calibrator_intrinsic_params):
    pinhole_calibrator_intrinsic_params = generate_pinhole_calibrator_intrinsic_params

    dir_save_detect_result = Path(pinhole_calibrator_intrinsic_params["dir_save_detect_result"])
    dir_save_detect_result = None
    dir_imgs = Path(pinhole_calibrator_intrinsic_params["dir_calib_images"])
    path_imgs = list(dir_imgs.glob("intrinsic*.jpg"))

    chessboard_detector = ChessboardDetector(chessboard_size=(6, 7))
    pinhole_calibrator = PinholeCalibrator(intrinsic_detector=chessboard_detector)

    rms, mtx, dist, rvecs, tvecs = pinhole_calibrator.calibrate_intrinsic(
        images=path_imgs, dir_save_detect_result=dir_save_detect_result
    )
    assert np.allclose(mtx, pinhole_calibrator_intrinsic_params["K"], atol=1e-3)
    assert np.allclose(dist, pinhole_calibrator_intrinsic_params["D"], atol=1e-3)


# def test_apply_intrinsic():
#     target_mtx = np.array([[534.15663136, 0.0, 341.71479628], [0.0, 534.25492559, 232.05013999], [0.0, 0.0, 1.0]])
#     target_dist = np.array([[-2.94269293e-01, 1.23247845e-01, 1.13850492e-03, -1.38021876e-04, 1.02084844e-02]])
#     dir_save_detect_result=Path("tmp/pinhole")
#     dir_save_detect_result=None
#     dir_save = Path("tmp/pinhole")

#     chessboard_detector = ChessboardDetector(chessboard_size=(6, 7))
#     pinhole_calibrator = PinholeCalibrator(detector=chessboard_detector)
#     dir_imgs = Path("sample_data/camera/pinhole_calibrator")
#     path_imgs = list(dir_imgs.glob("intrinsic*.jpg"))
#     rms, mtx, dist, rvecs, tvecs = pinhole_calibrator.calibrate_intrinsic(images=path_imgs,dir_save_detect_result=dir_save_detect_result)
#     pinhole_calibrator.apply_intrinsic(images=path_imgs,dir_save=dir_save)


def test_calibrate_extrinsic(generate_pinhole_calibrator_extrinsic_params):
    pinhole_calibrator_extrinsic_params = generate_pinhole_calibrator_extrinsic_params

    pinhole_calibrator = PinholeCalibrator()
    pinhole_calibrator.set_intrinsic_matrix(pinhole_calibrator_extrinsic_params["K"])
    pinhole_calibrator.set_intrinsic_dist(pinhole_calibrator_extrinsic_params["D"])

    rms, rvec_cw, tvec_cw = pinhole_calibrator.calibrate_extrinsic(
        pinhole_calibrator_extrinsic_params["img_points"], pinhole_calibrator_extrinsic_params["obj_points"]
    )
    assert np.allclose(rvec_cw, pinhole_calibrator_extrinsic_params["rvec_cw"], atol=1e-3)
    assert np.allclose(tvec_cw, pinhole_calibrator_extrinsic_params["tvec_cw"], atol=1e-3)


def test_generate_map_transform_pixel_points_to_world_points(generate_pinhole_calibrator_extrinsic_params):
    pinhole_calibrator_extrinsic_params = generate_pinhole_calibrator_extrinsic_params

    R_mat, _ = cv2.Rodrigues(pinhole_calibrator_extrinsic_params["rvec_cw"])
    R_wc = R_mat.T
    t_wc = -R_mat.T @ pinhole_calibrator_extrinsic_params["tvec_cw"]

    pinhole_calibrator = PinholeCalibrator()
    xyz_map = pinhole_calibrator.generate_map_transform_pixel_points_to_world_points(
        pinhole_calibrator_extrinsic_params["K"],
        pinhole_calibrator_extrinsic_params["D"],
        R_wc,
        t_wc,
        pinhole_calibrator_extrinsic_params["image_size"],
        plane_z=-0.07,
    )
    assert np.allclose(xyz_map[290, 270], [2.50, 0.288, -0.07], atol=0.05)
