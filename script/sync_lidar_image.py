import shutil
from pathlib import Path
import bisect


def parse_timestamp(filename: str) -> int:
    """
    从文件名解析时间戳
    1768372206_973804235_sensor_msgs__msg__PointCloud2.pcd
    -> ns timestamp
    """
    parts = filename.split("_")
    sec = int(parts[0])
    nsec = int(parts[1])
    return sec * 1_000_000_000 + nsec


def build_image_index(image_dir: Path):
    """
    构建 image timestamp 索引
    """
    image_files = sorted(image_dir.glob("*.jpg"))

    timestamps = []
    paths = []

    for f in image_files:
        ts = parse_timestamp(f.name)
        timestamps.append(ts)
        paths.append(f)

    return timestamps, paths


def find_nearest(ts_list, target):
    """
    二分查找最近时间
    """
    idx = bisect.bisect_left(ts_list, target)

    if idx == 0:
        return 0
    if idx == len(ts_list):
        return len(ts_list) - 1

    before = ts_list[idx - 1]
    after = ts_list[idx]

    if abs(before - target) < abs(after - target):
        return idx - 1
    else:
        return idx


def sync_images(pcd_dir, image_dir, output_dir, max_diff_ns=100_000_000):
    """
    主同步函数

    max_diff_ns:
        最大允许时间差 (默认100ms)
    """

    pcd_dir = Path(pcd_dir)
    image_dir = Path(image_dir)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    print("Building image index...")
    img_ts, img_paths = build_image_index(image_dir)

    print(f"Total images: {len(img_paths)}")

    pcd_files = sorted(pcd_dir.glob("*.pcd"))
    print(f"Total pcd: {len(pcd_files)}")

    matched = 0
    skipped = 0
    errors = []

    for pcd in pcd_files:

        pcd_ts = parse_timestamp(pcd.name)

        idx = find_nearest(img_ts, pcd_ts)

        img_ts_match = img_ts[idx]
        img_path = img_paths[idx]

        diff = abs(img_ts_match - pcd_ts)

        if diff > max_diff_ns:
            skipped += 1
            continue

        new_name = pcd.stem + ".jpg"
        dst = output_dir / new_name

        shutil.copy2(img_path, dst)

        matched += 1
        errors.append(diff)

    print("\n==== Sync Result ====")
    print("matched:", matched)
    print("skipped:", skipped)

    if errors:
        print("max error (ms):", max(errors) / 1e6)
        print("mean error (ms):", sum(errors) / len(errors) / 1e6)


if __name__ == "__main__":

    pcd_dir = "/home/ubuntu/Desktop/project/2601_3DLidar_object_detect/datasets/26-01-15-gaoxinhuayuan-lidar/msg_gaoxinhuayuan_26-01-15/rslidar_points"
    image_dir = "/home/ubuntu/Desktop/project/2601_3DLidar_object_detect/datasets/26-01-15-gaoxinhuayuan-lidar/msg_gaoxinhuayuan_26-01-15/rgbd_front_rgb0_image"
    output_dir = "/home/ubuntu/Desktop/project/2601_3DLidar_object_detect/datasets/26-01-15-gaoxinhuayuan-lidar/msg_gaoxinhuayuan_26-01-15/synced_images"

    sync_images(pcd_dir, image_dir, output_dir)