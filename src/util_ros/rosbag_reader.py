from pathlib import Path
from collections import defaultdict
import cv2
from rosbags.highlevel import AnyReader
from rosbags.image import message_to_cvimage
from rosbags.typesys import Stores, get_typestore
from rosbags.typesys.store import Typestore

from .message_saver import MessageSaver


class RosbagReader:
    def __init__(
        self,
        bag_path: str,
        topics: list,
        typestore: Typestore = get_typestore(Stores.ROS2_KILTED),
        message_saver: MessageSaver = MessageSaver(),
        start_time: float = 0.0,
        end_time: float = None,
    ):
        """
        初始化 RosbagReader
        :param bag_path: rosbag 文件路径
        :param topics: 提取的 ROS 话题列表
        :param start_time: 提取的起始时间（秒）
        :param end_time: 提取的结束时间（秒）
        """
        self.bag_path = Path(bag_path)
        self.topics = topics
        self.typestore = typestore
        self.message_saver = message_saver
        self.start_time = start_time
        self.end_time = end_time if end_time else float("inf")

    def save_msg(self, dir_save: Path | str):
        # 逐条读取ros消息
        # 检查topic是否在存储列表中
        with AnyReader([self.bag_path], default_typestore=self.typestore) as reader:
            connections = [x for x in reader.connections if x.topic in self.topics]
            for connection, timestamp, rawdata in reader.messages(
                connections=connections
            ):
                msg = reader.deserialize(rawdata, connection.msgtype)

                print(msg.header.frame_id)
