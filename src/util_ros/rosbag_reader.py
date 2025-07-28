from pathlib import Path
from typing import Union
from rosbags.highlevel import AnyReader
from rosbags.typesys import Stores, get_typestore
from rosbags.typesys.store import Typestore

from .message_saver import MessageSaver


class RosbagReader:
    def __init__(
        self,
        bag_path: Union[str, Path],
        topics: list,
        typestore: Typestore = get_typestore(Stores.ROS2_KILTED),
        message_saver: MessageSaver = MessageSaver(),
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

    # def save_msg(self, dir_save: Path | str):
    #     # 检查topic是否在存储列表中
    #     with AnyReader([self.bag_path], default_typestore=self.typestore) as reader:
    #         connections = [x for x in reader.connections if x.topic in self.topics]
    #         for connection, timestamp, rawdata in reader.messages(
    #             connections=connections
    #         ):
    #             msg = reader.deserialize(rawdata, connection.msgtype)
    #             path_file = self.message_saver.save(msg, dir_save, connection.topic)

    def save_msg(self, dir_save: Union[str, Path]):
        """
        保存消息到指定目录，按照 bag 名和 topic 分类存储。
        """
        # 获取 bag 的名称（ROS1 是文件名，ROS2 是文件夹名）
        bag_name = self._get_bag_name()

        # 目标保存路径：<dir_save>/<bag_name>/<topic_name>
        save_dir = Path(dir_save) / bag_name

        with AnyReader([self.bag_path], default_typestore=self.typestore) as reader:
            # 获取符合 topic 的消息连接
            connections = [x for x in reader.connections if x.topic in self.topics]

            for connection, timestamp, rawdata in reader.messages(
                connections=connections
            ):
                msg = reader.deserialize(rawdata, connection.msgtype)
                # 为每个话题创建保存路径并保存消息
                # topic_save_dir = save_dir / connection.topic
                path_file = self.message_saver.save(
                    msg, str(save_dir), connection.topic
                )

    def get_info(self):

        pass

    def print_info(self):
        pass

    def _get_bag_name(self) -> str:
        """
        根据 rosbag 类型返回 bag 名
        - 对于 ROS1，返回文件名（去扩展名）
        - 对于 ROS2，返回文件夹名
        """
        if self.bag_path.suffix == ".bag":  # ROS1
            return self.bag_path.stem  # 获取文件名，不含扩展名
        elif self.bag_path.is_dir():  # ROS2
            return self.bag_path.name  # 获取文件夹名
        else:
            raise ValueError("Invalid rosbag path")
