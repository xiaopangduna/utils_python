import numpy as np
from rosbags.typesys import get_typestore, Stores
from rosbags.typesys.types import (
    builtin_interfaces__msg__Time,
    std_msgs__msg__Header,
)



# 构造一个Image消息
# 构造一个Imu消息

def get_msg_sensor_msgs_msg_Image():

    # --------------------------
    # 1. 配置图像参数
    # --------------------------
    height = 240  # 图像高度（像素）
    width = 320   # 图像宽度（像素）
    encoding = "rgb8"  # 编码格式：每个像素3字节（R、G、B）
    is_bigendian = 0   # 小端字节序（常见于x86架构）
    pixel_bytes = 3    # 根据编码计算：rgb8 → 3字节/像素

    # step = 一行的总字节数 = width * 每个像素字节数
    step = width * pixel_bytes

    # --------------------------
    # 2. 生成模拟图像数据（示例：红色渐变图像）
    # --------------------------
    # 方法1：用numpy生成渐变数据（简单直观）
    # 创建一个 (height, width, 3) 的数组，R通道随x递增，G/B为0
    data_np = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            # R通道：x越大越亮（0→255），G和B为0 → 红色渐变
            data_np[y, x, 0] = int(255 * x / width)  # R
            data_np[y, x, 1] = 0                      # G
            data_np[y, x, 2] = 0                      # B
    # 转换为字节数组（rosbags的data字段需要bytes类型）
    image_data = data_np.tobytes()

    # --------------------------
    # 3. 构造Header（时间戳和坐标系）
    # --------------------------
    header = std_msgs__msg__Header(
        stamp=builtin_interfaces__msg__Time(sec=1620000000, nanosec=123456789),  # 时间戳
        frame_id="test_camera"  # 相机坐标系ID
    )

    # --------------------------
    # 4. 构造sensor_msgs/Image消息
    # --------------------------
    # 获取ROS2的类型存储（含sensor_msgs/msg/Image定义）
    typestore = get_typestore(Stores.ROS1_NOETIC)
    # 获取Image消息类型
    Image = typestore.get_type("sensor_msgs/msg/Image")

    # 实例化图像消息
    image_msg = Image(
        header=header,
        height=height,
        width=width,
        encoding=encoding,
        is_bigendian=is_bigendian,
        step=step,
        data=image_data  # 图像像素数据
    )
    return image_msg




# 1. 获取 ROS2 Foxy 的类型存储（含标准消息定义）
typestore = get_typestore(Stores.ROS2_FOXY)

# 2. 获取 sensor_msgs/Imu 消息类型类
Imu = typestore.get_type('sensor_msgs/msg/Imu')  # ROS2 消息格式（注意 msg 路径）
# 若为 ROS1，类型名为 'sensor_msgs/Imu'（无 msg 子路径）
# Imu = typestore.get_type('sensor_msgs/Imu')

# 3. 构造消息字段（嵌套字段需逐层实例化）
# 3.1 构造 header 字段（std_msgs/Header）
Header = typestore.get_type('std_msgs/msg/Header')
header = Header(
    stamp=builtin_interfaces__msg__Time(sec=1620000000, nanosec=123456789),  # 时间戳
    frame_id='imu_link'  # 坐标系 ID
)

# 3.2 构造 Imu 消息并设置字段
imu_msg = Imu(
    header=header,
    # 设置惯性测量数据（示例值）
    orientation={
        'x': 0.0,
        'y': 0.0,
        'z': 0.0,
        'w': 1.0
    },
    orientation_covariance=[0.0]*9,  # 9元素列表（ covariance 矩阵）
    angular_velocity={
        'x': 0.1,
        'y': 0.2,
        'z': 0.3
    },
    angular_velocity_covariance=[0.0]*9,
    linear_acceleration={
        'x': 9.8,
        'y': 0.0,
        'z': 0.0
    },
    linear_acceleration_covariance=[0.0]*9
)

# 4. 验证消息（打印字段）
print("构造的 Imu 消息：")
print(f"Frame ID: {imu_msg.header.frame_id}")
print(f"Linear Acceleration: {imu_msg.linear_acceleration.x}, {imu_msg.linear_acceleration.y}, {imu_msg.linear_acceleration.z}")

# 5.（可选）序列化消息（用于写入 rosbag 或传输）
# 需指定消息类型，这里 Imu 对应的 msgtype 为 'sensor_msgs/msg/Imu'（ROS2）
serialized_data = typestore.serialize(imu_msg, 'sensor_msgs/msg/Imu')
print(f"序列化后的数据长度：{len(serialized_data)} 字节")


