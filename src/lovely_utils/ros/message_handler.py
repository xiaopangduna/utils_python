import os
import cv2
import numpy as np
from abc import ABC, abstractmethod
from rosbags.image import message_to_cvimage
import struct


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


class SensorMsgsMsgPointCloud2Handler(MessageHandler):
    def __init__(self, format: str = "pcd", data_format: str = "ascii"):
        super().__init__(format)  # 调用基类构造函数来初始化 format
        self.data_format = data_format.lower()  # 新增属性，控制PCD数据保存格式，默认为ascii

    def can_handle(self, msg) -> bool:
        # 判断是否为点云消息
        return (
            hasattr(msg, "header") 
            and hasattr(msg, "height")
            and hasattr(msg, "width")
            and hasattr(msg, "fields")
            and hasattr(msg, "data")
            and hasattr(msg, "is_bigendian")
            and hasattr(msg, "point_step")
            and hasattr(msg, "row_step")
            and hasattr(msg, "is_dense")
        )

    def save(self, msg, output_dir: str, topic_name: str) -> str:
        # 生成文件名
        file_name = self._generate_file_name(msg)
        # 更改扩展名为pcd（点云数据文件）
        base_name, _ = os.path.splitext(file_name)
        file_name = f"{base_name}.pcd"
        file_path = self._generate_file_path(output_dir, topic_name, file_name)

        try:
            # 将PointCloud2消息转换为PCD格式并保存
            pcd_content = self._convert_to_pcd(msg)
            
            # 根据数据格式选择保存方式
            if self.data_format == "binary":
                with open(file_path, 'wb') as f:
                    f.write(pcd_content)
            else:  # 默认ascii格式
                with open(file_path, 'w') as f:
                    f.write(pcd_content)
                    
            return file_path
        except Exception as e:
            print(f"保存点云消息失败: {e}")
            return None

    def _convert_to_pcd(self, msg):
        """将ROS PointCloud2消息转换为PCD格式，支持ascii和binary格式"""
        # 解析字段信息
        field_names = []
        field_offsets = []
        field_types = []
        
        for field in msg.fields:
            field_names.append(field.name)
            field_offsets.append(field.offset)
            field_types.append(field.datatype)
        
        # 读取点云数据
        data = msg.data
        width = msg.width
        height = msg.height
        point_step = msg.point_step
        num_points = width * height
        
        # 根据数据格式设置头部
        if self.data_format == "binary":
            # 构建二进制格式的PCD头部
            pcd_header = f"""# .PCD v0.7 - Point Cloud Data file format
VERSION 0.7
FIELDS {' '.join(field_names)}
SIZE {' '.join([str(self._get_size_by_type(ft)) for ft in field_types])}
TYPE {' '.join([self._get_type_char(ft) for ft in field_types])}
COUNT {' '.join(['1'] * len(field_names))}
WIDTH {num_points}
HEIGHT 1
VIEWPOINT 0 0 0 1 0 0 0
POINTS {num_points}
DATA binary
"""
            # 构建二进制数据部分
            points_data_bytes = bytearray()
            for i in range(num_points):
                point_start_idx = i * point_step
                for j, field_name in enumerate(field_names):
                    offset = field_offsets[j]
                    field_type = field_types[j]
                    
                    # 根据数据类型解析字段
                    value = self._parse_field_value(data, point_start_idx + offset, field_type)
                    
                    # 将值转换回对应的二进制格式
                    if field_type == 1:  # INT8
                        points_data_bytes.extend(struct.pack('<b', value))
                    elif field_type == 2:  # UINT8
                        points_data_bytes.extend(struct.pack('<B', value))
                    elif field_type == 3:  # INT16
                        points_data_bytes.extend(struct.pack('<h', value))
                    elif field_type == 4:  # UINT16
                        points_data_bytes.extend(struct.pack('<H', value))
                    elif field_type == 5:  # INT32
                        points_data_bytes.extend(struct.pack('<i', value))
                    elif field_type == 6:  # UINT32
                        points_data_bytes.extend(struct.pack('<I', value))
                    elif field_type == 7:  # FLOAT32
                        points_data_bytes.extend(struct.pack('<f', value))
                    elif field_type == 8:  # FLOAT64
                        points_data_bytes.extend(struct.pack('<d', value))
            
            # 组合头部和数据
            full_pcd = pcd_header.encode('utf-8') + points_data_bytes
            return full_pcd
        else:  # 默认ascii格式
            # 构建ASCII格式的PCD头部
            pcd_header = f"""# .PCD v0.7 - Point Cloud Data file format
VERSION 0.7
FIELDS {' '.join(field_names)}
SIZE {' '.join([str(self._get_size_by_type(ft)) for ft in field_types])}
TYPE {' '.join([self._get_type_char(ft) for ft in field_types])}
COUNT {' '.join(['1'] * len(field_names))}
WIDTH {num_points}
HEIGHT 1
VIEWPOINT 0 0 0 1 0 0 0
POINTS {num_points}
DATA ascii
"""
            
            # 解析数据
            points_data = []
            for i in range(num_points):
                point_start_idx = i * point_step
                point_data = []
                
                for j, field_name in enumerate(field_names):
                    offset = field_offsets[j]
                    field_type = field_types[j]
                    
                    # 根据数据类型解析字段
                    value = self._parse_field_value(data, point_start_idx + offset, field_type)
                    point_data.append(str(value))
                
                points_data.append(' '.join(point_data))
            
            # 合并头部和数据
            full_pcd = pcd_header + '\n'.join(points_data)
            return full_pcd

    def _get_size_by_type(self, field_type):
        """根据字段类型返回字节大小"""
        if field_type in [1, 2]:  # INT8, UINT8
            return 1
        elif field_type in [3, 4]:  # INT16, UINT16
            return 2
        elif field_type in [5, 6, 7]:  # INT32, UINT32, FLOAT32
            return 4
        elif field_type == 8:  # FLOAT64
            return 8
        return 4  # 默认大小

    def _get_type_char(self, field_type):
        """根据字段类型返回字符标识"""
        if field_type in [1, 2, 3, 4, 5, 6]:  # 整数类型
            return 'I'
        elif field_type in [7, 8]:  # 浮点类型
            return 'F'
        return 'F'  # 默认浮点类型

    def _parse_field_value(self, data, offset, field_type):
        """解析字段值"""
        if field_type == 1:  # INT8
            return struct.unpack_from('<b', data, offset)[0]
        elif field_type == 2:  # UINT8
            return struct.unpack_from('<B', data, offset)[0]
        elif field_type == 3:  # INT16
            return struct.unpack_from('<h', data, offset)[0]
        elif field_type == 4:  # UINT16
            return struct.unpack_from('<H', data, offset)[0]
        elif field_type == 5:  # INT32
            return struct.unpack_from('<i', data, offset)[0]
        elif field_type == 6:  # UINT32
            return struct.unpack_from('<I', data, offset)[0]
        elif field_type == 7:  # FLOAT32
            return struct.unpack_from('<f', data, offset)[0]
        elif field_type == 8:  # FLOAT64
            return struct.unpack_from('<d', data, offset)[0]
        
        # 默认处理方式
        return 0


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