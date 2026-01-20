from pathlib import Path
from typing import Union, Literal, Optional
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

    def save_msg(self, dir_save: Optional[Path] = None):
        """
        保存消息到指定目录，按照 bag 名和 topic 分类存储。
        """
        bag_name = self._get_bag_name()
        if dir_save is None:
            save_dir = self.bag_path.parent / bag_name
        else:
            save_dir = Path(dir_save) / bag_name

        with AnyReader([self.bag_path], default_typestore=self.typestore) as reader:
            # 获取符合 topic 的消息连接
            connections = [x for x in reader.connections if x.topic in self.topics]
            
            # 如果没有找到匹配的话题，则提前返回
            if not connections:
                print(f"Warning: No connections found for topics: {self.topics}")
                return
            
            for connection, timestamp, rawdata in reader.messages(
                connections=connections
            ):

                msg = reader.deserialize(rawdata, connection.msgtype)
                handler = self.message_saver.get_handler(msg)
                handler.save(msg, str(save_dir), connection.topic)
        return

    @staticmethod
    def get_info(
        path_bag: Path, typestore: Typestore = get_typestore(Stores.ROS1_NOETIC)
    ):
        info = RosbagReader._get_info_dict(path_bag, typestore=typestore)
        info_str = RosbagReader._format_info(info)
        return info_str

    def _get_bag_name(self) -> str:
        """
        根据 rosbag 类型返回 bag 名
        - 对于 ROS1，返回文件名（去扩展名）
        - 对于 ROS2，返回文件夹名
        """
        if self.bag_path.suffix == ".bag":  # ROS1
            return "msg_" + self.bag_path.stem  # 获取文件名，不含扩展名
        elif self.bag_path.is_dir():  # ROS2
            return "msg_" + self.bag_path.name  # 获取文件夹名
        else:
            raise ValueError("Invalid rosbag path")

    @staticmethod
    def _get_info_dict(
        path_bag: Path, typestore: Typestore = get_typestore(Stores.ROS1_NOETIC)
    ) -> dict:
        """
        获取 rosbag 信息
        :param path_bag: rosbag 文件路径
        :param typestore: Typestore for deserializing messages
        :return: dict
        """
        info = {}

        with AnyReader([path_bag], default_typestore=typestore) as reader:
            # Basic bag information
            info["path"] = str(path_bag)
            info["start_time"] = reader.start_time
            info["end_time"] = reader.end_time
            info["duration"] = (
                reader.end_time - reader.start_time
                if reader.start_time and reader.end_time
                else None
            )

            # Topic information
            topics_info = {}
            for connection in reader.connections:
                topic = connection.topic
                if topic not in topics_info:
                    topics_info[topic] = {
                        "type": connection.msgtype,
                        "count": 0,
                        "connections": 0,
                    }
                topics_info[topic]["count"] += 1
                topics_info[topic]["connections"] = len(
                    [c for c in reader.connections if c.topic == topic]
                )

            # Count messages per topic
            for topic in topics_info:
                topic_connections = [c for c in reader.connections if c.topic == topic]
                message_count = sum(
                    1 for _ in reader.messages(connections=topic_connections)
                )
                topics_info[topic]["message_count"] = message_count

            info["topics"] = topics_info
            info["total_messages"] = sum(
                topic_info["message_count"] for topic_info in topics_info.values()
            )
            info["total_topics"] = len(topics_info)

        return info

    @staticmethod
    def _format_info(info: dict, align: int = 30) -> str:
        """
        将 bag info 格式化为可读字符串。
        每个 topic 占据一行，便于快速浏览。
        """
        lines = []
        lines.append(f"Bag Path: {info['path']}")
        lines.append(f"Start Time: {info['start_time']}")
        lines.append(f"End Time: {info['end_time']}")
        lines.append(f"Duration: {info['duration']:.2f} s")
        lines.append(f"Total Topics: {info['total_topics']}")
        lines.append(f"Total Messages: {info['total_messages']}")
        lines.append("Topics:")

        for topic, topic_info in info["topics"].items():
            topic_str = topic.ljust(align)
            type_str = f"[{topic_info['type']}]".ljust(35)
            msg_str = f"Messages: {topic_info['message_count']}".ljust(20)
            conn_str = f"Connections: {topic_info['connections']}"
            lines.append(f"  {topic_str} {type_str} {msg_str} {conn_str}")

        return "\n".join(lines)