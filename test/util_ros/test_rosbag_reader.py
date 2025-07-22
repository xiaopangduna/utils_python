import sys
import pytest
from util_ros import RosbagReader


def test_rosbag_reader():
    # 测试能否正常获取数据
    bag_path = "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/250507_zhongshi_c50a_calibr/2025-05-07-16-57-04.bag"
    topics = ["/camera/image_raw"]
    start_time = 0.0
    end_time = None
    reader = RosbagReader(bag_path, topics, start_time, end_time)
    for topic, msg, t in reader.iter_msg():
        print(topic, msg, t)
    # reader.extract_data()

# def test_rosbag_reader_with_time():
#     bag_path = "../data/rosbag/test.bag"
#     topics = ["/camera/image_raw"]
#     start_time = 0.0
#     end_time = None
#     reader = RosbagReader(bag_path, topics, start_time, end_time)
#     reader.extract_data()

# def test_rosbag_reader_extract_data():
#     bag_path = "../data/rosbag/test.bag"
#     topics = ["/camera/image_raw"]
#     start_time = 0.0
#     end_time = None
#     reader = RosbagReader(bag_path, topics, start_time, end_time)
#     reader.extract_data()