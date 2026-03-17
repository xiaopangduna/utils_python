import cv2
from cv2 import aruco
import os
from pathlib import Path


def detect_charuco_folder(
    input_dir,
    output_dir,
    board_size=(5, 7),
    square_length=0.04,
    marker_length=0.02,
):

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ArUco dictionary
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)

    # 创建Charuco Board
    board = aruco.CharucoBoard(
        board_size,
        square_length,
        marker_length,
        aruco_dict,
    )

    # Aruco detector
    detector = aruco.ArucoDetector(aruco_dict)

    # 支持图片格式
    image_extensions = [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]

    images = [
        f for f in input_dir.iterdir()
        if f.suffix.lower() in image_extensions
    ]

    print(f"Found {len(images)} images")

    for img_path in images:

        image = cv2.imread(str(img_path))

        if image is None:
            print(f"Failed to read {img_path}")
            continue

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 1 detect markers
        corners, ids, rejected = detector.detectMarkers(gray)

        if ids is not None:

            # draw markers
            aruco.drawDetectedMarkers(image, corners, ids)

            # 2 interpolate charuco
            ret, charuco_corners, charuco_ids = aruco.interpolateCornersCharuco(
                corners,
                ids,
                gray,
                board,
            )

            if charuco_ids is not None:

                aruco.drawDetectedCornersCharuco(
                    image,
                    charuco_corners,
                    charuco_ids,
                )

                print(
                    f"{img_path.name}: detected {len(charuco_ids)} charuco corners"
                )
            else:
                print(f"{img_path.name}: no charuco corners")

        else:
            print(f"{img_path.name}: no markers")

        # 保存结果
        save_path = output_dir / img_path.name
        cv2.imwrite(str(save_path), image)

    print("Done.")


if __name__ == "__main__":

    input_folder = "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2026-03-13-标定板选型/不同距离下的标定板"
    output_folder = "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2026-03-13-标定板选型/output_detected"

    detect_charuco_folder(
        input_folder,
        output_folder,
        board_size=(4, 3),
        square_length=0.20,
        marker_length=0.12,
    )