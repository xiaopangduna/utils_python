from pathlib import Path
from typing import Any, Optional, Union
import os
import cv2
import numpy as np

from .base_calibrator import BaseCalibrator
from ..detector.base_detector import BaseDetector


class PinholeCalibrator(BaseCalibrator):
    def __init__(self, intrinsic_detector: BaseDetector = None, extrinsic_detector: BaseDetector = None) -> None:
        super().__init__(intrinsic_detector, extrinsic_detector)
        self.image_size = None

    def set_intrinsic_matrix(self, intrinsic_matrix: Any):
        """
        设置内参矩阵
        :param intrinsic_matrix: 内参矩阵 (3x3)
        """
        self.intrinsic_matrix = intrinsic_matrix

    def set_intrinsic_dist(self, dist_coeffs: Any):
        """
        设置畸变系数
        :param dist_coeffs: 畸变系数 (5x1)
        """
        self.intrinsic_dist = dist_coeffs

    def set_extrinsic_rvec_cw(self, extrinsic_rvec_cw: Any):
        """
        设置外参旋转向量（相机坐标系到世界坐标系的旋转）
        :param extrinsic_rvec_cw: 外参旋转向量 (3x1)
        """
        self.extrinsic_rvec_cw = extrinsic_rvec_cw

    def set_extrinsic_tvec_cw(self, extrinsic_tvec_cw: Any):
        """
        设置外参平移向量（相机坐标系到世界坐标系的平移）
        :param extrinsic_tvec_cw: 外参平移向量 (3x1)
        """
        self.extrinsic_tvec_cw = extrinsic_tvec_cw

    def set_image_size(self, image_size: tuple[int, int]):
        """
        设置图像尺寸
        :param image_size: 图像尺寸 (width, height)
        """
        self.image_size = image_size

    def calibrate_intrinsic(
        self, images: list[Path], dir_save_detect_result: Path = None, remove_unvalid_image: bool = True, **kwargs
    ) -> None:
        """
        Calibrate the camera.
        """
        images = [Path(img) for img in images]
        valid_images = []
        images_without_corners = []
        img_points = []
        obj_points = []

        for path_img in images:
            if path_img.exists() and path_img.is_file():
                valid_images.append(path_img)
            else:
                print(f"Warning: unvalid image file - {path_img}")
        if not valid_images:
            return None, None, None, None, None

        # 2. 准备保存目录（若需要）
        if dir_save_detect_result:
            try:
                dir_save_detect_result.mkdir(parents=True, exist_ok=True)  # 递归创建目录
            except OSError as e:
                raise IOError(f"无法创建保存目录 {dir_save_detect_result}: {str(e)}")

        self.img_size = cv2.imread(valid_images[0]).shape[:2][::-1]  # (width, height)
        for path_img in valid_images:
            img = cv2.imread(path_img)
            img_point, obj_point, image_with_corners = self.intrinsic_detector.detect(img)
            if img_point is not None and obj_point is not None:
                img_points.append(img_point)
                obj_points.append(obj_point)
                if dir_save_detect_result:
                    cv2.imwrite(str(dir_save_detect_result / path_img.name), image_with_corners)
            if img_point is None:
                images_without_corners.append(path_img)

        if remove_unvalid_image and images_without_corners:
            for path_img in images_without_corners:
                print(f"Removing image without corners: {path_img}")
                os.remove(path_img)

        if not img_points or not obj_points:
            return None, None, None, None, None

        rms, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, self.img_size, None, None)
        self.intrinsic_matrix = mtx
        self.intrinsic_dist = dist
        return rms, mtx, dist, rvecs, tvecs

    def apply_intrinsic(self, images: list[Path], dir_save: Path, **kwargs) -> None:
        """
        Apply the intrinsic calibration to the camera.
        """
        images = [Path(img) for img in images]
        for path_img in images:
            img = cv2.imread(path_img)
            # dst = cv2.undistort(img, self.intrinsic_matrix, self.dist_coeffs, None, self.intrinsic_matrix)
            h, w = img.shape[:2]
            newcameramtx1, roi = cv2.getOptimalNewCameraMatrix(
                self.intrinsic_matrix, self.intrinsic_dist, (w, h), 1, (w, h)
            )
            dst1 = cv2.undistort(img, self.intrinsic_matrix, self.intrinsic_dist, None, newcameramtx1)
            # newcameramtx2, roi = cv2.getOptimalNewCameraMatrix(self.intrinsic_matrix, self.dist_coeffs, (w,h), 0, (w,h))
            # dst2 = cv2.undistort(img, self.intrinsic_matrix, self.dist_coeffs, None, newcameramtx2)
            cv2.imwrite(str(dir_save / (path_img.stem + "_undistort" + path_img.suffix)), dst1)
        return

    def calibrate_extrinsic(self, img_points: Union[np.ndarray, Path], obj_points: np.ndarray, **kwargs):
        """
        Calibrate the camera.
        """
        undistorted_pts = cv2.undistortPoints(
            img_points.reshape(-1, 1, 2), self.intrinsic_matrix, self.intrinsic_dist, P=self.intrinsic_matrix
        )
        undistorted_pts = undistorted_pts.reshape(-1, 2)
        retval, self.extrinsic_rvex_cw, self.extrinsic_tvec_cw = cv2.solvePnP(
            obj_points, undistorted_pts, self.intrinsic_matrix, None, flags=cv2.SOLVEPNP_ITERATIVE
        )
        if not retval:
            return None, None, None
        img_points_proj, _ = cv2.projectPoints(
            obj_points,
            self.extrinsic_rvex_cw,
            self.extrinsic_tvec_cw,
            self.intrinsic_matrix,
            distCoeffs=self.intrinsic_dist,
        )
        img_points_proj = img_points_proj.reshape(-1, 2)
        rms_pixel = cv2.norm(img_points.reshape(-1, 2), img_points_proj, cv2.NORM_L2) / len(obj_points)
        return rms_pixel, self.extrinsic_rvex_cw, self.extrinsic_tvec_cw

    def apply_extrinsic(self, obj_points: np.ndarray, **kwargs) -> None:
        """
        Apply the extrinsic calibration to the camera.
        """
        img_points_proj, _ = cv2.projectPoints(
            obj_points,
            self.extrinsic_rvex_cw,
            self.extrinsic_tvec_cw,
            self.intrinsic_matrix,
            distCoeffs=self.intrinsic_dist,
        )
        return img_points_proj.reshape(-1, 2)

    @staticmethod
    def generate_map_transform_pixel_points_to_world_points(K, D, R_wc, t_wc, image_size, plane_z=0.0) -> None:
        """
        Generate the map transform pixel points to world points.
        """
        H, W = image_size
        xyz_map = np.zeros((H, W, 3), dtype=np.float32)

        # 像素坐标网格
        u, v = np.meshgrid(np.arange(W), np.arange(H))  # shape: (H, W)
        pixel_coords = np.stack([u, v], axis=-1).astype(np.float32)  # (H, W, 2)
        pixel_coords_flat = pixel_coords.reshape(-1, 1, 2)

        # 去畸变得到归一化相机坐标
        undistorted_pts = cv2.undistortPoints(pixel_coords_flat, K, D)  # (N,1,2)
        undistorted_pts = undistorted_pts.reshape(-1, 2)

        # 单位射线
        rays_cam = np.concatenate([undistorted_pts, np.ones((undistorted_pts.shape[0], 1))], axis=1)

        # 相机坐标系 → 世界坐标系的射线方向
        rays_world = (R_wc @ rays_cam.T).T  # (N,3)

        # ✅ 正确计算相机中心
        cam_center = t_wc.flatten()  # shape (3,)

        # 与 z=plane_z 的平面求交
        t_vals = (plane_z - cam_center[2]) / rays_world[:, 2]
        pts_world = cam_center + rays_world * t_vals[:, np.newaxis]

        xyz_map = pts_world.reshape(H, W, 3).astype(np.float32)
        return xyz_map

    @staticmethod
    def save_map(map: np.ndarray, path_save: Path, datatype=np.float32) -> None:
        """
        Save the map to a file.
        """
        if map.dtype != np.float32:
            map = map.astype(datatype)

        # 写入二进制文件
        with open(path_save, "wb") as f:
            f.write(map.tobytes())
            print(f"Map saved to {path_save}")

    @staticmethod
    def load_map(path_map: Path, shape: tuple[int, int, int], datatype=np.float32) -> np.ndarray:
        """
        Load the map from a file.
        """
        if not path_map.exists():
            raise FileNotFoundError(f"Map file {path_map} does not exist.")

        # 读取二进制文件
        with open(path_map, "rb") as f:
            data = f.read()
            map = np.frombuffer(data, dtype=datatype).reshape(shape)
            print(f"Map loaded from {path_map}")
            return map

    @staticmethod
    def validate_map(
        img_points: np.ndarray,
        obj_points: np.ndarray,
        xyz_map: np.ndarray,
    ) -> None:
        """
        分析像素坐标对应的世界坐标，并计算投影误差

        :param img_points: 图像特征点坐标列表/数组 (Nx2)
        :param obj_points: 世界坐标系特征点坐标列表/数组 (Nx3)
        :param xyz_map: 像素到世界坐标的映射矩阵 (HxWx3)
        :param save_bin_path: 保存xyz_map二进制文件的路径（为None则不保存）
        :return: 距离误差列表和平均误差
        """
        # 确保输入是numpy数组格式
        img_points = np.array(img_points) if not isinstance(img_points, np.ndarray) else img_points
        obj_points = np.array(obj_points) if not isinstance(obj_points, np.ndarray) else obj_points

        # 检查输入维度是否匹配
        if len(img_points) != len(obj_points):
            raise ValueError(f"图像点与世界点数量不匹配: {len(img_points)} vs {len(obj_points)}")

        # 打印像素坐标对应的世界坐标
        print("像素坐标对应的世界坐标:")
        for px, obj_p in zip(img_points, obj_points):
            # 转换为整数像素坐标（四舍五入）
            u, v = int(round(px[0])), int(round(px[1]))

            # 获取映射的世界坐标和实际世界坐标
            x, y, z = xyz_map[v, u]
            x_obj, y_obj, z_obj = obj_p

            # 格式化输出（保留3位小数）
            print(
                f"Pixel ({v}, {u}) → 映射坐标: ({x:.3f}, {y:.3f}, {z:.3f}) | 实际坐标: ({x_obj:.3f}, {y_obj:.3f}, {z_obj:.3f})"
            )

        # 计算投影误差
        reprojected_world_points = []

        for px in img_points:
            u, v = int(round(px[0])), int(round(px[1]))
            if 0 <= v < xyz_map.shape[0] and 0 <= u < xyz_map.shape[1]:
                pt_world = xyz_map[v, u]  # 注意顺序是[y, x]
                reprojected_world_points.append(pt_world)
            else:
                reprojected_world_points.append([np.nan, np.nan, np.nan])  # 越界处理

        reprojected_world_points = np.array(reprojected_world_points)
        dist_errors = np.linalg.norm(obj_points - reprojected_world_points, axis=1)
        mean_error = np.nanmean(dist_errors)

        # 打印误差结果
        print("\n📏 3D 世界坐标误差 (单位：米):")
        for i, err in enumerate(dist_errors):
            print(f"  点 {i+1}: 距离误差 = {err:.4f} m")
        print(f"  平均距离误差 = {mean_error:.4f} m")

        return

    @staticmethod
    def invert_pose_transform(R: np.ndarray, t: np.ndarray) -> tuple:
        """
        对相机与世界坐标系间的位姿变换求逆（双向转换）。

        参数:
        - R: 旋转矩阵 (3,3)（若is_cw=True，则为相机→世界的旋转；否则为世界→相机的旋转）
        - t: 平移向量 (3,)（同上）
        - is_cw: 输入变换是否为“相机→世界”（cw: camera→world）

        返回:
        - R_inv: 逆变换的旋转矩阵（若输入是cw，则返回wc的旋转；反之亦然）
        - t_inv: 逆变换的平移向量（同上）
        """
        R_inv = R.T
        t_inv = -R.T @ t
        return R_inv, t_inv
