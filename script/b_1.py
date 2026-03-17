import cv2
import apriltag
from pathlib import Path


def detect_apriltag_folder(input_dir, output_dir):

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 创建 AprilTag detector
    options = apriltag.DetectorOptions(
        families="tag36h11"   # Kalibr AprilGrid 通常用这个
    )
    detector = apriltag.Detector(options)

    image_ext = [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]

    images = [p for p in input_dir.iterdir() if p.suffix.lower() in image_ext]

    print(f"Found {len(images)} images")

    for img_path in images:

        image = cv2.imread(str(img_path))

        if image is None:
            print(f"Failed to read {img_path}")
            continue

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 检测 AprilTag
        results = detector.detect(gray)

        print(f"{img_path.name}: detected {len(results)} tags")

        for r in results:

            corners = r.corners.astype(int)
            center = tuple(r.center.astype(int))

            # 画四条边
            for i in range(4):
                pt1 = tuple(corners[i])
                pt2 = tuple(corners[(i + 1) % 4])
                cv2.line(image, pt1, pt2, (0, 255, 0), 2)

            # 画中心
            cv2.circle(image, center, 5, (0, 0, 255), -1)

            # 写 ID
            cv2.putText(
                image,
                str(r.tag_id),
                (corners[0][0], corners[0][1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2
            )

        save_path = output_dir / img_path.name
        cv2.imwrite(str(save_path), image)

    print("Detection finished.")


if __name__ == "__main__":

    detect_apriltag_folder(
        "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2026-03-13-标定板选型/不同距离下的标定板",
        "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2026-03-13-标定板选型/apriltag_1"
    )