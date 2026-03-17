import cv2
import numpy as np
from pathlib import Path
from pupil_apriltags import Detector


def detect_aprilgrid_folder(input_dir, output_dir):

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    detector = Detector(
        families="tag36h11",
        nthreads=4,
        quad_decimate=1.0,
        quad_sigma=0.0,
        refine_edges=1
    )

    image_ext = [".png", ".jpg", ".jpeg", ".bmp"]
    images = [p for p in input_dir.iterdir() if p.suffix.lower() in image_ext]

    print(f"Found {len(images)} images")

    for img_path in images:

        img = cv2.imread(str(img_path))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        tags = detector.detect(gray)

        print(f"{img_path.name}: detected {len(tags)} tags")

        for tag in tags:

            corners = tag.corners.astype(int)

            # 画 tag 边框
            for i in range(4):
                cv2.line(
                    img,
                    tuple(corners[i]),
                    tuple(corners[(i+1)%4]),
                    (0,255,0),
                    2
                )

            # 画中心
            cx, cy = int(tag.center[0]), int(tag.center[1])
            cv2.circle(img, (cx,cy), 4, (0,0,255), -1)

            # 写ID
            cv2.putText(
                img,
                str(tag.tag_id),
                (cx+5, cy+5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255,0,0),
                2
            )

        save_path = output_dir / img_path.name
        cv2.imwrite(str(save_path), img)

    print("Done")


if __name__ == "__main__":

    detect_aprilgrid_folder(
        "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2026-03-13-标定板选型/不同距离下的标定板",
        "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2026-03-13-标定板选型/apriltag_d"
    )