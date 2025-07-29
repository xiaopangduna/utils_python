from rosbags.typesys import Stores, get_typestore

from lovely_utils.ros.rosbag_reader import RosbagReader
from lovely_utils.ros.message_saver import MessageSaver

from .util import *


def test_print_info():
    # 测试能否正常获取数据
    pass


def test_save_msg_sensor_msgs_msg_Image(setup_typestore):
    # 测试能否正常获取数据
    typestore = setup_typestore
    bag_path = "/home/ubuntu/Desktop/project/utils_python/tmp/test.bag"
    get_ros1_bag_file(
        bag_filename=bag_path,
        topics=["/camera/color/image_raw", "/imu/data"],
        msg_types=["sensor_msgs/msg/Image", "sensor_msgs/msg/Imu"],
        typestore=typestore,
    )
    pass
    # message_saver = MessageSaver()
    # reader = RosbagReader(bag_path, topics, typestore, message_saver)
    # reader.save_msg("/home/ubuntu/Desktop/project/utils_python/tmp")


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
