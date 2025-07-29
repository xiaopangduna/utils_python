import os
import pytest
from typing import Tuple

import numpy as np
from rosbags.typesys import Stores, get_typestore
from rosbags.rosbag1 import Writer as ROS1BagWriter
from rosbags.serde import serialize_cdr

from typing import List


ROS_VERSION_MAPPING = {
    "ros1_noetic": Stores.ROS1_NOETIC,
    # "ros2_dashing": Stores.ROS2_DASHING,
    # "ros2_eloquent": Stores.ROS2_ELOQUENT,
    # "ros2_foxy": Stores.ROS2_FOXY,
    # "ros2_galactic": Stores.ROS2_GALACTIC,
    # "ros2_humble": Stores.ROS2_HUMBLE,
    # "ros2_iron": Stores.ROS2_IRON,
    # "ros2_jazzy": Stores.ROS2_JAZZY,
    # "ros2_kilted": Stores.ROS2_KILTED,
}

ROS_VERSION_PARAMS = list(ROS_VERSION_MAPPING.keys())  # 自动获取版本列表


@pytest.fixture(params=ROS_VERSION_PARAMS)
def setup_typestore(request):
    ros_version = request.param
    typestore = get_typestore(ROS_VERSION_MAPPING[ros_version])
    return typestore


@pytest.fixture
def setup_temp_dir(tmp_path):
    # 使用 tmp_path 夹具创建临时目录
    temp_dir = tmp_path / "tmp"
    temp_dir.mkdir()  # 创建子目录
    return temp_dir


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

    # 生成模拟图像数据
    if encoding == "rgb8":
        x_grid = np.tile(np.linspace(0, 255, width, dtype=np.uint8), (height, 1))
        data_np = np.zeros((height, width, 3), dtype=np.uint8)
        data_np[:, :, 0] = x_grid  # R通道
    elif encoding == "mono8":
        x_grid = np.tile(np.linspace(0, 255, width, dtype=np.uint8), (height, 1))
        data_np = x_grid.astype(np.uint8)
    else:
        data_np = np.zeros((height, width, pixel_bytes), dtype=np.uint8)

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


def get_msg_sensor_msgs_msg_Imu(
    typestore,
    timestamp: Tuple[int, int] = (1620000000, 123456789),
    frame_id: str = "test_imu",
    orientation: Tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0),
    angular_velocity: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    linear_acceleration: Tuple[float, float, float] = (0.0, 0.0, 9.81),
):
    """构建ROS的sensor_msgs/Imu消息"""
    # 创建消息头
    header = get_msg_sensor_msgs_msg_Header(typestore, timestamp, frame_id)

    # 创建四元数
    Quaternion = typestore.types["geometry_msgs/msg/Quaternion"]
    orientation_msg = Quaternion(
        x=orientation[0], y=orientation[1], z=orientation[2], w=orientation[3]
    )
    orientation_covariance = [0.0] * 9

    # 创建角速度
    Vector3 = typestore.types["geometry_msgs/msg/Vector3"]
    angular_velocity_msg = Vector3(
        x=angular_velocity[0], y=angular_velocity[1], z=angular_velocity[2]
    )
    angular_velocity_covariance = [0.0] * 9

    # 创建线性加速度
    linear_acceleration_msg = Vector3(
        x=linear_acceleration[0], y=linear_acceleration[1], z=linear_acceleration[2]
    )
    linear_acceleration_covariance = [0.0] * 9

    # 创建IMU消息
    Imu = typestore.types["sensor_msgs/msg/Imu"]
    imu_msg = Imu(
        header=header,
        orientation=orientation_msg,
        orientation_covariance=orientation_covariance,
        angular_velocity=angular_velocity_msg,
        angular_velocity_covariance=angular_velocity_covariance,
        linear_acceleration=linear_acceleration_msg,
        linear_acceleration_covariance=linear_acceleration_covariance,
    )

    return imu_msg

def get_ros1_bag_file(
    bag_filename: str,
    topics: List[str],
    msg_types: List[str],
    typestore,
    duration: float = 10.0,  # 持续时间（秒）
    frequency: float = 10.0,  # 发布频率（Hz）
    image_params: dict = None,  # 图像消息自定义参数
    imu_params: dict = None,   # IMU消息自定义参数
) -> None:
    """
    生成包含 sensor_msgs/msg/Image 和 sensor_msgs/msg/Imu 的 ROS1 bag 文件
    修复序列化错误，优化时间戳计算，支持自定义消息参数
    """
    # 初始化参数（默认空字典，避免None错误）
    image_params = image_params or {}
    imu_params = imu_params or {}

    # 1. 输入验证
    if len(topics) != len(msg_types):
        raise ValueError("topics与msg_types长度必须一致")
    
    supported_types = {"sensor_msgs/msg/Image", "sensor_msgs/msg/Imu"}
    for msg_type in msg_types:
        if msg_type not in supported_types:
            raise ValueError(f"仅支持{supported_types}，不支持{msg_type}")
        if msg_type not in typestore.types:
            raise ValueError(f"消息类型{msg_type}未在typestore中注册")

    # 2. 准备输出目录
    output_dir = os.path.dirname(bag_filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 3. 计算消息数量与时间戳（修复纳秒溢出问题）
    num_messages = int(duration * frequency)
    interval_ns = int(1e9 / frequency)  # 消息间隔（纳秒）
    start_total_ns = 1620000000 * 1_000_000_000 + 123456789  # 起始总纳秒数
    timestamps = []
    for i in range(num_messages):
        total_ns = start_total_ns + i * interval_ns
        sec = total_ns // 1_000_000_000
        nsec = total_ns % 1_000_000_000  # 确保nsec在0-999,999,999范围内
        timestamps.append((sec, nsec))

    # 4. 打开ROS1 bag写入器
    with ROS1BagWriter(bag_filename) as writer:
        # 4.1 创建话题连接（存储连接对象和消息类型）
        connections = {}
        for topic, msg_type in zip(topics, msg_types):
            # 为每个话题创建连接（ROS1 bag需要指定消息类型）
            conn = writer.add_connection(topic, msg_type)
            connections[topic] = (conn, msg_type)

        # 4.2 循环生成并写入消息
        for seq, (sec, nsec) in enumerate(timestamps):
            timestamp_ns = sec * 1_000_000_000 + nsec  # 写入用的纳秒时间戳
            timestamp = (sec, nsec)  # (秒, 纳秒)元组

            for topic, (conn, msg_type) in connections.items():
                try:
                    # 生成对应类型的消息
                    if msg_type == "sensor_msgs/msg/Image":
                        # 生成图像消息（确保data为numpy数组）
                        msg = get_msg_sensor_msgs_msg_Image(
                            typestore=typestore,
                            height=image_params.get("height", 240),
                            width=image_params.get("width", 320),
                            encoding=image_params.get("encoding", "rgb8"),
                            frame_id=image_params.get("frame_id", f"camera_{topic.split('/')[-1]}"),
                            timestamp=timestamp,
                        )
                        msg.header.seq = seq  # 更新序列号
                        msg.data = np.frombuffer(msg.data, dtype=np.uint8).ravel()

                    elif msg_type == "sensor_msgs/msg/Imu":
                        # 生成IMU消息
                        msg = get_msg_sensor_msgs_msg_Imu(
                            typestore=typestore,
                            timestamp=timestamp,
                            frame_id=imu_params.get("frame_id", f"imu_{topic.split('/')[-1]}"),
                            orientation=imu_params.get("orientation", (1.0, 0.0, 0.0, 0.0)),
                            angular_velocity=imu_params.get("angular_velocity", (0.0, 0.0, 0.0)),
                            linear_acceleration=imu_params.get("linear_acceleration", (0.0, 0.0, 9.81)),
                        )
                        msg.header.seq = seq  # 更新序列号
                        
                    # 序列化消息并写入（关键修复：依赖Image消息的data为numpy数组）
                    writer.write(conn, timestamp_ns, typestore.serialize_ros1(msg, msg_type),)

                except Exception as e:
                    raise RuntimeError(f"处理话题{topic}的第{seq}条消息失败: {str(e)}")

    print(f"成功生成ROS1 bag文件: {bag_filename}")
    print(f"  消息总数: {num_messages * len(topics)} | 持续时间: {duration}秒 | 频率: {frequency}Hz")
    print(f"  包含话题: {dict(zip(topics, msg_types))}")
    