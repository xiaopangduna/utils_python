import os
import cv2
import numpy as np
from abc import ABC, abstractmethod
from rosbags.image import message_to_cvimage


class MessageHandler(ABC):
    """消息处理器基类"""

    def __init__(self, format: str = "json"):  # 添加 format 属性
        self.format = format.lower()  # 初始化 format 属性

    @abstractmethod
    def can_handle(self, msg) -> bool:
        pass

    @abstractmethod
    def save(self, msg, output_dir: str, topic_name: str) -> str:
        pass

    def _get_message_type(self, msg) -> str:
        return getattr(msg, "_type", type(msg).__name__)

    def _generate_file_name(self, msg) -> str:
        # 时间戳转为字符串（秒_纳秒）
        timestamp = msg.header.stamp
        time_str = f"{timestamp.sec}_{timestamp.nanosec}"
        msg_type = self._get_message_type(msg)
        return f"{time_str}_{msg_type}.{self.format}"

    def _generate_file_path(
        self, output_dir: str, topic_name: str, filename: str
    ) -> str:
        topic_dir = os.path.join(output_dir, topic_name.strip("/").replace("/", "_"))
        os.makedirs(topic_dir, exist_ok=True)
        file_path = os.path.join(topic_dir, filename)
        return file_path


class SensorMsgsMsgImageHandler(MessageHandler):
    def __init__(self, format: str = "jpg"):
        super().__init__(format)  # 调用基类构造函数来初始化 format

    def can_handle(self, msg) -> bool:
        # 判断是否为图像消息（检查关键字段）
        return (
            hasattr(msg, "encoding")
            and hasattr(msg, "data")
            and hasattr(msg, "height")
            and hasattr(msg, "width")
        )

    def save(self, msg, output_dir: str, topic_name: str) -> str:
        # 生成文件名（时间戳+frame_id，根据编码格式判断）
        file_name = self._generate_file_name(msg)
        file_path = self._generate_file_path(output_dir, topic_name, file_name)

        try:
            # 用rosbags-image转换图像消息为numpy数组（OpenCV格式）
            cv_image = self._convert_to_cv(msg)
            # 保存为JPG
            cv2.imwrite(file_path, cv_image)
            return file_path
        except Exception as e:
            print(f"保存图像失败: {e}")
            return None

    def _convert_to_cv(self, image_msg):
        """用rosbags-image将ROS图像消息转换为OpenCV格式（BGR）"""
        img_array = message_to_cvimage(image_msg)

        # 使用字典简化通道转换
        encoding_map = {
            "rgb8": cv2.COLOR_RGB2BGR,
            "rgb16": cv2.COLOR_RGB2BGR,
            "bgr8": None,
            "bgra8": cv2.COLOR_BGRA2BGR,
            "mono8": None,
            "mono16": None,
        }

        encoding = image_msg.encoding.lower()
        if encoding in encoding_map:
            if encoding_map[encoding]:
                return cv2.cvtColor(img_array, encoding_map[encoding])
            return img_array
        else:
            return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)  # 假设默认是RGB


class GenericMessageHandler(MessageHandler):
    """处理非图像消息（保存为JSON）"""

    def __init__(self, format: str = "json"):
        super().__init__(format)  # 调用基类构造函数来初始化 format

    def can_handle(self, msg) -> bool:
        return True

    def save(self, msg, output_dir: str, topic_name: str) -> str:
        import json

        file_name = self._generate_file_name(msg)
        file_path = self._generate_file_path(output_dir, topic_name, file_name)
        try:
            msg_dict = self._message_to_dict(msg)
            with open(file_path, "w") as f:
                json.dump(msg_dict, f, indent=2)
            return file_path
        except Exception as e:
            print(f"保存消息失败: {e}")
            return None

    def _message_to_dict(self, msg) -> dict:
        result = {}
        for field in dir(msg):
            if field.startswith("_"):
                continue
            value = getattr(msg, field)
            if isinstance(value, (int, float, str, bool)):
                result[field] = value
            elif hasattr(value, "__dict__"):
                result[field] = self._message_to_dict(value)
            else:
                result[field] = str(value)
        return result
