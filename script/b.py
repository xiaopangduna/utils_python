import cv2
from cv2 import aruco
from pathlib import Path


def detect_apriltag_folder(input_dir, output_dir):

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # AprilTag dictionary
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_APRILTAG_36h11)

    parameters = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(aruco_dict, parameters)

    image_ext = [".png", ".jpg", ".jpeg", ".bmp"]

    images = [p for p in input_dir.iterdir() if p.suffix.lower() in image_ext]

    print(f"Found {len(images)} images")

    for img_path in images:

        image = cv2.imread(str(img_path))

        if image is None:
            print(f"Failed to read {img_path}")
            continue

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # detect markers
        corners, ids, rejected = detector.detectMarkers(gray)

        # ---------- 画成功检测 ----------
        if ids is not None:
            print(f"{img_path.name}: detected {len(ids)} tags")
            aruco.drawDetectedMarkers(image, corners, ids)
        else:
            print(f"{img_path.name}: detected 0 tags")

        # ---------- 画 rejected ----------
        if rejected is not None and len(rejected) > 0:

            for r in rejected:
                pts = r.reshape((4, 2)).astype(int)

                for i in range(4):
                    pt1 = tuple(pts[i])
                    pt2 = tuple(pts[(i + 1) % 4])
                    cv2.line(image, pt1, pt2, (0, 0, 255), 2)

        print(f"{img_path.name}: rejected {0 if rejected is None else len(rejected)}")

        save_path = output_dir / img_path.name
        cv2.imwrite(str(save_path), image)

    print("Done.")


if __name__ == "__main__":

    detect_apriltag_folder(
        "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2026-03-13-标定板选型/不同距离下的标定板",
        "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2026-03-13-标定板选型/apriltag"
    )