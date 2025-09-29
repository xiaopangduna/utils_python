from pathlib import Path
from rosbags.typesys import Stores, get_typestore
from lovely_utils.ros.rosbag_reader import RosbagReader
from lovely_utils.ros.message_saver import MessageSaver


import os
import pytest
from typing import Tuple

import numpy as np
from PIL import Image
from rosbags.typesys import Stores, get_typestore
from rosbags.rosbag1 import Writer as ROS1BagWriter
from rosbags.serde import serialize_cdr

from typing import List, Union

def extract_msg_from_rosbag():
    path_bag = "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2025-07-28-office-808-test_RGB_D/2025-07-28-14-35-20.bag"
    path_bag = Path(path_bag)
    topics = ["/topic1", "/topic2"]
    save_dir = "output_dir"
    message_saver = MessageSaver()
    ros_version = Stores.ROS1_NOETIC if "bag" in path_bag.suffix else Stores.ROS2_HUMBLE
    typestore = get_typestore(ros_version)
    reader = RosbagReader(
        path_bag, topics, typestore=typestore, message_saver=message_saver
    )
    reader.save_msg(save_dir)


def get_rosbag_info():
    path_bag = "/home/ubuntu/Desktop/tmp/hk_2025-08-01/rosbag2_2025_07_31-12_02_42"
    path_bag = Path(path_bag)
    ros_version = Stores.ROS1_NOETIC if "bag" in path_bag.suffix else Stores.ROS2_HUMBLE
    typestore = get_typestore(ros_version)
    info = RosbagReader.get_info(path_bag, typestore=typestore)
    print(info)


def get_msg_sensor_msgs_msg_Header(
    typestore, timestamp: Tuple[int, int], frame_id: str
):
    """创建sensor_msgs/Header消息头"""
    Time = typestore.types["builtin_interfaces/msg/Time"]
    Header = typestore.types["std_msgs/msg/Header"]
    header = Header(
        seq=0,
        stamp=Time(sec=timestamp[0], nanosec=timestamp[1]),
        frame_id=frame_id,
    )
    return header


def get_msg_sensor_msgs_msg_Image(
    typestore,
    height: int = 240,
    width: int = 320,
    encoding: str = "rgb8",
    frame_id: str = "test_camera",
    timestamp: Tuple[int, int] = (1620000000, 123456789),
):
    """构建ROS sensor_msgs/Image消息"""
    # 验证输入参数
    if height <= 0 or width <= 0:
        raise ValueError("图像高度和宽度必须为正整数")

    # 根据编码确定每个像素的字节数
    pixel_bytes_map = {"rgb8": 3, "bgr8": 3, "mono8": 1, "rgba8": 4, "mono16": 2}
    pixel_bytes = pixel_bytes_map.get(encoding, None)
    if pixel_bytes is None:
        raise ValueError(f"不支持的编码格式: {encoding}")

    # 计算每行字节数
    step = width * pixel_bytes

    data_np = generate_image_data(
        height=height, width=width, encoding=encoding, pixel_bytes=pixel_bytes
    )
    # 创建消息头
    header = get_msg_sensor_msgs_msg_Header(typestore, timestamp, frame_id)
    image_data = data_np.tobytes()
    # 实例化图像消息
    Image = typestore.types["sensor_msgs/msg/Image"]
    image_msg = Image(
        header=header,
        height=height,
        width=width,
        encoding=encoding,
        is_bigendian=0,
        step=step,
        data=image_data,
    )

    return image_msg


if __name__ == "__main__":
    get_rosbag_info()
    # extract_msg_from_rosbag()
