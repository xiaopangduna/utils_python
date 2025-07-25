import sys
import pytest

from util_ros.rosbag_reader import RosbagReader
from util_ros.message_saver import MessageSaver
from rosbags.typesys import Stores, get_typestore
from rosbags.typesys.store import Typestore

def test_save_msg_sensor_msgs_msg_Image():
    # 测试能否正常获取数据
    bag_path = "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/250507_zhongshi_c50a_calibr/2025-05-07-16-57-04.bag"
    topics = ["/ascamera_hp60c/rgb0/image"]
    start_time = 0.0
    end_time = None
    typestore = get_typestore(Stores.ROS2_KILTED)
    message_saver = MessageSaver()
    reader = RosbagReader(bag_path, topics, typestore, message_saver, start_time, end_time) 
    reader.save_msg("/home/ubuntu/Desktop/tmp")
    # reader.extract_data()

# def test_save_sensor_msgs_msg_Image():
#     # 测试能否正常获取数据
#     bag_path = "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/250507_zhongshi_c50a_calibr/2025-05-07-16-57-04.bag"
#     topics = ["/ascamera_hp60c/rgb0/image"]
#     start_time = 0.0
#     end_time = None
#     typestore = get_typestore(Stores.ROS2_KILTED)
#     message_saver = MessageSaver()
#     reader = RosbagReader(bag_path, topics, typestore, message_saver, start_time, end_time) 
#     reader.save_msg("/home/ubuntu/Desktop/tmp")
#     # reader.extract_data()

# def test_save_sensor_msgs_msg_Image():
#     # 测试能否正常获取数据
#     bag_path = "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/250507_zhongshi_c50a_calibr/2025-05-07-16-57-04.bag"
#     topics = ["/ascamera_hp60c/rgb0/image"]
#     start_time = 0.0
#     end_time = None
#     typestore = get_typestore(Stores.ROS2_KILTED)
#     message_saver = MessageSaver()
#     reader = RosbagReader(bag_path, topics, typestore, message_saver, start_time, end_time) 
#     reader.save_msg("/home/ubuntu/Desktop/tmp")
#     # reader.extract_data()