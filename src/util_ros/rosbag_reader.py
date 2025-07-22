
from pathlib import Path
import rosbag
from collections import defaultdict
import cv2
from rosbags.highlevel import AnyReader
from rosbags.image import message_to_cvimage
from rosbags.typesys import Stores, get_typestore
from rosbags.typesys.store import Typestore

class RosbagReader:
    def __init__(self, bag_path: str, topics: list, start_time: float = 0.0, end_time: float = None,typestore: Stores = Stores.ROS2_KILTED):
        """
        初始化 RosbagExtractor
        :param bag_path: rosbag 文件路径
        :param topics: 提取的 ROS 话题列表
        :param start_time: 提取的起始时间（秒）
        :param end_time: 提取的结束时间（秒）
        """
        self.bag_path = bag_path
        self.topics = topics
        self.start_time = start_time
        self.end_time = end_time if end_time else float('inf')
        self.typestore = get_typestore(typestore)
        # self.dir_save = Path(r"/home/ubuntu/Desktop/tmp")


    def save_msg(self,dir_save: Path):
        """
        使用生成器逐条提取数据
        """
        with rosbag.Bag(self.bag_path, 'r') as bag:
            for topic, msg, t in bag.read_messages(topics=self.topics):
                if self.start_time <= t.to_sec() <= self.end_time:
                    # 使用生成器逐条返回数据
                    yield topic, self.msg_handler.handle_message(topic, msg)
