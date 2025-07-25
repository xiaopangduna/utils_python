import os
import cv2
import numpy as np
from abc import ABC, abstractmethod
from rosbags.typesys.types import builtin_interfaces__msg__Time
from rosbags.image import message_to_cvimage

class MessageHandler(ABC):
    """消息处理器基类"""
    @abstractmethod
    def can_handle(self, msg) -> bool:
        pass
    @abstractmethod
    def save(self, msg, output_dir: str, topic_name: str) -> str:
        pass


class SensorMsgsMsgImageHandler(MessageHandler):
    def can_handle(self, msg) -> bool:
        # 判断是否为图像消息（检查关键字段）
        return hasattr(msg, 'encoding') and hasattr(msg, 'data') and hasattr(msg, 'height') and hasattr(msg, 'width')
    
    def save(self, msg, output_dir: str, topic_name: str) -> str:
        # 创建话题目录（用话题名作为文件夹）
        topic_dir = os.path.join(output_dir, topic_name.strip('/').replace('/', '_'))
        os.makedirs(topic_dir, exist_ok=True)
        
        # 生成文件名（时间戳+frame_id，根据编码格式判断）
        filename = self._generate_filename(msg)
        file_path = os.path.join(topic_dir, filename)
        
        try:
            # 用rosbags-image转换图像消息为numpy数组（OpenCV格式）
            cv_image = self._convert_to_cv(msg)
            # 保存为JPG
            cv2.imwrite(file_path, cv_image)
            return file_path
        except Exception as e:
            print(f"保存图像失败: {e}")
            return None
    
    def _generate_filename(self, image_msg) -> str:
        # 时间戳转为字符串（秒_纳秒）
        timestamp = image_msg.header.stamp
        time_str = f"{timestamp.sec}_{timestamp.nanosec}"
        
        # 若编码为RGB且有frame_id，文件名格式：时间戳_frame_id.jpg
        is_rgb = image_msg.encoding.lower() in ["rgb8", "rgb16"]
        if is_rgb and image_msg.header.frame_id:
            safe_frame_id = image_msg.header.frame_id.replace('/', '_').replace(':', '_')
            return f"{time_str}_{safe_frame_id}.jpg"
        else:
            return f"{time_str}.jpg"
    
    def _convert_to_cv(self, image_msg):
        """用rosbags-image将ROS图像消息转换为OpenCV格式（BGR）"""
        # 转换为numpy数组（rosbags-image返回的是通道顺序与编码一致的数组）
        # 例如：rgb8编码返回 (H, W, 3) 的RGB数组；bgr8返回BGR数组
        img_array = message_to_cvimage(image_msg)
        
        # 根据编码调整通道顺序（OpenCV保存JPG需要BGR格式）
        encoding = image_msg.encoding.lower()
        if encoding in ["rgb8", "rgb16"]:
            # RGB转BGR
            return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        elif encoding in ["bgr8", "bgra8"]:
            # 已为BGR或BGRA，直接返回（BGRA需转BGR）
            return cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR) if encoding == "bgra8" else img_array
        elif encoding in ["mono8", "mono16"]:
            # 单通道灰度图，若为16位需转为8位
            if img_array.dtype == np.uint16:
                return (img_array / 256).astype(np.uint8)  # 16→8位
            return img_array
        else:
            # 其他编码默认转为BGR
            return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)  # 假设默认是RGB


class GenericMessageHandler(MessageHandler):
    """处理非图像消息（保存为JSON）"""
    def __init__(self, format: str = "json"):
        self.format = format.lower()
    
    def can_handle(self, msg) -> bool:
        return True  # 通用处理器，最后兜底
    
    def save(self, msg, output_dir: str, topic_name: str) -> str:
        import json
        topic_dir = os.path.join(output_dir, topic_name.strip('/').replace('/', '_'))
        os.makedirs(topic_dir, exist_ok=True)
        
        msg_type = self._get_message_type(msg)
        timestamp = getattr(msg.header, 'stamp', builtin_interfaces__msg__Time(sec=0, nanosec=0))
        time_str = f"{timestamp.sec}_{timestamp.nanosec}"
        filename = f"{time_str}_{msg_type.replace('/', '_')}.{self.format}"
        file_path = os.path.join(topic_dir, filename)
        
        try:
            msg_dict = self._message_to_dict(msg)
            with open(file_path, 'w') as f:
                json.dump(msg_dict, f, indent=2)
            return file_path
        except Exception as e:
            print(f"保存消息失败: {e}")
            return None
    
    def _get_message_type(self, msg) -> str:
        return getattr(msg, '_type', type(msg).__name__)
    
    def _message_to_dict(self, msg) -> dict:
        result = {}
        for field in dir(msg):
            if field.startswith('_'):
                continue
            value = getattr(msg, field)
            if isinstance(value, (int, float, str, bool)):
                result[field] = value
            elif isinstance(value, builtin_interfaces__msg__Time):
                result[field] = {'sec': value.sec, 'nanosec': value.nanosec}
            elif hasattr(value, '__dict__'):
                result[field] = self._message_to_dict(value)
            else:
                result[field] = str(value)
        return result



# 使用示例
if __name__ == "__main__":
    # 创建保存器
    saver = MessageSaver(output_dir="/home/ubuntu/Desktop/project/utils_python/tmp")
    
    # 生成测试图像消息
    from rosbags.typesys import get_typestore, Stores
    from rosbags.typesys.types import std_msgs__msg__Header, sensor_msgs__msg__Image
    
    # 获取ROS1图像消息类型
    typestore = get_typestore(Stores.ROS1_NOETIC)
    Image = typestore.types["sensor_msgs/msg/Image"]
    
    # 构造Header
    header = std_msgs__msg__Header(
        stamp=builtin_interfaces__msg__Time(sec=1620000000, nanosec=123456789),
        frame_id="camera_optical_frame"
    )
    
    # 生成RGB8测试图像（红色渐变）
    height, width = 480, 640
    data_np = np.zeros((height, width, 3), dtype=np.uint8)
    data_np[:, :, 0] = np.linspace(0, 255, width, dtype=np.uint8)  # R通道渐变
    image_data = data_np.tobytes()
    
    # 构造图像消息
    image_msg = Image(
        header=header,
        height=height,
        width=width,
        encoding="rgb8",
        is_bigendian=0,
        step=width * 3,
        data=image_data
    )
    
    # 保存图像消息
    file_path = saver.save_message(image_msg, "/camera/color/image_raw")
    print(f"图像保存路径: {file_path}")