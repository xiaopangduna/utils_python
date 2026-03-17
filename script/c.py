import cv2
from cv2 import aruco

image_path = "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2026-03-13-标定板选型/不同距离下的标定板/Snipaste_2026-03-13_15-52-28.png"

img = cv2.imread(image_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# OpenCV支持的所有字典
dictionaries = {
    "DICT_4X4_50": aruco.DICT_4X4_50,
    "DICT_4X4_100": aruco.DICT_4X4_100,
    "DICT_4X4_250": aruco.DICT_4X4_250,
    "DICT_4X4_1000": aruco.DICT_4X4_1000,
    "DICT_5X5_50": aruco.DICT_5X5_50,
    "DICT_5X5_100": aruco.DICT_5X5_100,
    "DICT_5X5_250": aruco.DICT_5X5_250,
    "DICT_5X5_1000": aruco.DICT_5X5_1000,
    "DICT_6X6_50": aruco.DICT_6X6_50,
    "DICT_6X6_100": aruco.DICT_6X6_100,
    "DICT_6X6_250": aruco.DICT_6X6_250,
    "DICT_6X6_1000": aruco.DICT_6X6_1000,
    "DICT_7X7_50": aruco.DICT_7X7_50,
    "DICT_7X7_100": aruco.DICT_7X7_100,
    "DICT_7X7_250": aruco.DICT_7X7_250,
    "DICT_7X7_1000": aruco.DICT_7X7_1000,
    "DICT_APRILTAG_16h5": aruco.DICT_APRILTAG_16h5,
    "DICT_APRILTAG_25h9": aruco.DICT_APRILTAG_25h9,
    "DICT_APRILTAG_36h10": aruco.DICT_APRILTAG_36h10,
    "DICT_APRILTAG_36h11": aruco.DICT_APRILTAG_36h11,
}

results = []

for name, dict_id in dictionaries.items():

    dictionary = aruco.getPredefinedDictionary(dict_id)
    detector = aruco.ArucoDetector(dictionary)

    corners, ids, rejected = detector.detectMarkers(gray)

    count = 0 if ids is None else len(ids)

    results.append((name, count))

    print(f"{name}: {count}")

# 找到检测最多的
best = max(results, key=lambda x: x[1])

print("\nMost likely dictionary:")
print(best)