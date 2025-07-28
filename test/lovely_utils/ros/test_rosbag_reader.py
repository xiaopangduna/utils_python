import sys
import pytest

from rosbags.typesys import Stores, get_typestore
from rosbags.typesys.store import Typestore

from lovely_utils.ros.rosbag_reader import RosbagReader
from lovely_utils.ros.message_saver import MessageSaver



# TODO 显示bag的信息
def test_print_info():
    # 测试能否正常获取数据
    pass


def test_save_msg_sensor_msgs_msg_Image():
    # 测试能否正常获取数据
    bag_path = "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/250507_zhongshi_c50a_calibr/2025-05-07-16-57-04.bag"
    topics = ["/ascamera_hp60c/rgb0/image"]
    typestore = get_typestore(Stores.ROS1_NOETIC)
    message_saver = MessageSaver()
    reader = RosbagReader(bag_path, topics, typestore, message_saver)
    reader.save_msg("/home/ubuntu/Desktop/project/utils_python/tmp")


def test_save_msg_sensor_msgs_msg_CameraInfo():
    bag_path = "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2025-07-24-office-808/2025-07-24-11-16-53.bag"
    topics = ["/nuwa_1/depth0/camera_info", "/nuwa_1/rgb0/camera_info"]
    typestore = get_typestore(Stores.ROS1_NOETIC)
    message_saver = MessageSaver()
    reader = RosbagReader(bag_path, topics, typestore, message_saver)
    reader.save_msg("/home/ubuntu/Desktop/project/utils_python/tmp")


def test_save_sensor_msgs_msg_Image_and_CameraInfo():
    bag_path = "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2025-07-28-office-808-test_RGB_D/2025-07-28-14-35-20.bag"
    topics = [
        "/nuwa_1/rgb0/image",
        "/nuwa_1/rgb0/camera_info",
    ]
    typestore = get_typestore(Stores.ROS1_NOETIC)
    message_saver = MessageSaver()
    reader = RosbagReader(bag_path, topics, typestore, message_saver)
    reader.save_msg("/home/ubuntu/Desktop/project/utils_python/tmp")
