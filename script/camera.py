import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R


def generate_pixel_to_world_map(K, D, R_wc, t_wc, image_size, plane_z=0.0):
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
    rays_cam = np.concatenate(
        [undistorted_pts, np.ones((undistorted_pts.shape[0], 1))], axis=1
    )

    # 相机坐标系 → 世界坐标系的射线方向
    rays_world = (R_wc @ rays_cam.T).T  # (N,3)

    # ✅ 正确计算相机中心
    cam_center = t_wc.flatten()  # shape (3,)

    # 与 z=plane_z 的平面求交
    t_vals = (plane_z - cam_center[2]) / rays_world[:, 2]
    pts_world = cam_center + rays_world * t_vals[:, np.newaxis]

    xyz_map = pts_world.reshape(H, W, 3).astype(np.float32)
    return xyz_map


def save_xyz_map_binary(xyz_map: np.ndarray, file_path: str):
    # 确保是 float32 类型，等价于 CV_32FC3
    if xyz_map.dtype != np.float32:
        xyz_map = xyz_map.astype(np.float32)

    # 写入二进制文件
    with open(file_path, "wb") as f:
        f.write(xyz_map.tobytes())


def load_xyz_map_binary(
    file_path: str, height: int = 480, width: int = 640
) -> np.ndarray:
    """
    加载用 save_xyz_map_binary 保存的二进制XYZ地图

    参数:
        file_path: 二进制文件路径
        height: 原始数组的高度（行数）
        width: 原始数组的宽度（列数）

    返回:
        xyz_map: 形状为 (height, width, 3) 的 np.float32 数组
    """
    # 读取二进制数据
    with open(file_path, "rb") as f:
        data = f.read()

    # 转换为np.float32数组，并reshape为 (height, width, 3)
    xyz_map = np.frombuffer(data, dtype=np.float32).reshape(height, width, 3)

    return xyz_map


def compute_world_projection_errors(img_points, obj_points, xyz_map):
    """
    计算像素反投影到世界坐标后，与原始3D目标点之间的欧式距离误差。

    参数:
    - img_points: (N, 2) 图像中的像素点，二维数组。
    - obj_points: (N, 3) 对应的世界坐标点，三维数组。
    - xyz_map: (H, W, 3) 每个像素对应的世界坐标反投影结果。

    返回:
    - dist_errors: 每个点的欧式距离误差（单位：米）
    - mean_error: 平均误差
    """
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

    return dist_errors, mean_error


if __name__ == "__main__":
    generate_pixel_to_world_map()
