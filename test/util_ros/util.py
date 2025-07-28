import numpy as np
from rosbags.typesys import get_typestore, Stores

def get_msg_sensor_msgs_msg_Image(
    height: int = 240,
    width: int = 320,
    encoding: str = "rgb8",
    frame_id: str = "test_camera",
    timestamp: tuple[int, int] = (1620000000, 123456789),
) -> "rosbags.typesys.types.sensor_msgs__msg__Image":
    """构建ROS 1的sensor_msgs/Image消息"""
    # 获取ROS 1的类型存储
    typestore = get_typestore(Stores.ROS1_NOETIC)
    # 验证输入参数
    if height <= 0 or width <= 0:
        raise ValueError("图像高度和宽度必须为正整数")

    # 根据编码确定每个像素的字节数
    pixel_bytes = {"rgb8": 3, "bgr8": 3, "mono8": 1, "rgba8": 4, "mono16": 2}.get(
        encoding, None
    )

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

    # 转换为字节数组
    image_data = data_np.tobytes()

    # 构造Header
    Time = typestore.types["builtin_interfaces/msg/Time"]
    Header = typestore.types["std_msgs/msg/Header"]
    Image = typestore.types["sensor_msgs/msg/Image"]

    header = Header(
        seq=0,
        stamp=Time(sec=timestamp[0], nanosec=timestamp[1]),
        frame_id=frame_id,
    )
    # 实例化图像消息
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


# # 1. 获取 ROS2 Foxy 的类型存储（含标准消息定义）
# typestore = get_typestore(Stores.ROS2_FOXY)

# # 2. 获取 sensor_msgs/Imu 消息类型类
# Imu = typestore.get_type('sensor_msgs/msg/Imu')  # ROS2 消息格式（注意 msg 路径）
# # 若为 ROS1，类型名为 'sensor_msgs/Imu'（无 msg 子路径）
# # Imu = typestore.get_type('sensor_msgs/Imu')

# # 3. 构造消息字段（嵌套字段需逐层实例化）
# # 3.1 构造 header 字段（std_msgs/Header）
# Header = typestore.get_type('std_msgs/msg/Header')
# header = Header(
#     stamp=builtin_interfaces__msg__Time(sec=1620000000, nanosec=123456789),  # 时间戳
#     frame_id='imu_link'  # 坐标系 ID
# )

# # 3.2 构造 Imu 消息并设置字段
# imu_msg = Imu(
#     header=header,
#     # 设置惯性测量数据（示例值）
#     orientation={
#         'x': 0.0,
#         'y': 0.0,
#         'z': 0.0,
#         'w': 1.0
#     },
#     orientation_covariance=[0.0]*9,  # 9元素列表（ covariance 矩阵）
#     angular_velocity={
#         'x': 0.1,
#         'y': 0.2,
#         'z': 0.3
#     },
#     angular_velocity_covariance=[0.0]*9,
#     linear_acceleration={
#         'x': 9.8,
#         'y': 0.0,
#         'z': 0.0
#     },
#     linear_acceleration_covariance=[0.0]*9
# )

# # 4. 验证消息（打印字段）
# print("构造的 Imu 消息：")
# print(f"Frame ID: {imu_msg.header.frame_id}")
# print(f"Linear Acceleration: {imu_msg.linear_acceleration.x}, {imu_msg.linear_acceleration.y}, {imu_msg.linear_acceleration.z}")

# # 5.（可选）序列化消息（用于写入 rosbag 或传输）
# # 需指定消息类型，这里 Imu 对应的 msgtype 为 'sensor_msgs/msg/Imu'（ROS2）
# serialized_data = typestore.serialize(imu_msg, 'sensor_msgs/msg/Imu')
# print(f"序列化后的数据长度：{len(serialized_data)} 字节")
