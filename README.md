# Lovely Utils

`lovely_utils` 是一个 Python 工具包，主要用于处理 ROS（机器人操作系统）相关的功能，如从 ROS bag 文件中提取消息、消息保存、相机校准等。同时，还提供了视频处理和文件处理的功能，并支持命令行接口，方便用户调用。

---

## ✨ 功能概述

- **ROS Bag 消息提取**：从 ROS bag 文件中提取指定话题的消息，并保存到指定目录。
- **消息保存**：支持多种消息类型的保存，如图像消息保存为图片，其他消息保存为 JSON 文件。
- **相机校准**：支持针孔相机与棋盘格的相机内参标定。
- **视频处理**：支持视频帧提取、图像合并为视频。
- **文件处理**：支持批量文件重命名和复制。

---

## 📦 安装

### 依赖安装

确保你已安装 Python 3.12 或更高版本，然后执行：

```bash
pip install -r requirements.txt
```

### 项目安装

使用 `setuptools` 安装：

```bash
python setup.py install
```

---

## 🚀 使用方法

### 命令行接口（CLI）

安装后可直接通过 `lovely_utils` 命令使用。

#### 提取 ROS Bag 消息

```bash
lovely_utils rosbag save \
  --bag-paths /path/to/your.bag \
  --topics /camera/image_raw \
  --topics /camera/camera_info \
  --save-dir ./output
```

#### 查看 ROS Bag 信息

```bash
lovely_utils rosbag info \
  --bag-path /path/to/your.bag \
  --topics /camera/image_raw
```

---

### Python 脚本调用示例

#### 提取 ROS Bag 消息

```python
from lovely_utils.ros.rosbag_reader import RosbagReader
from lovely_utils.ros.message_saver import MessageSaver

bag_path = "/path/to/your.bag"
topics = ["/camera/image_raw", "/camera/camera_info"]
save_dir = "./output"

message_saver = MessageSaver()
reader = RosbagReader(bag_path, topics, message_saver=message_saver)
reader.save_msg(save_dir)
```

#### 视频处理

```python
from lovely_utils.video_processor import VideoProcessor
from pathlib import Path
import cv2

# 视频帧提取
video_processor = VideoProcessor()
video_processor.extract_frame_from_video(
    path_video="input.avi",
    path_save="frames_output/"
)

# 图像合并为视频
processor = VideoProcessor()
processor.merge_image_to_video(
    dir_image=Path("frames_output/"),
    path_video=Path("output.avi"),
    img_size=(640, 480),
    fourcc=cv2.VideoWriter_fourcc(*"XVID"),
    frame_rate=5,
    fn=lambda x: int(x.stem.split("_")[-1])
)
```

#### 文件批量重命名

```python
from lovely_utils.file_processor import FileProcessor

processor = FileProcessor()
processor.rename_file(
    path_input="/input_dir",
    path_output="/output_dir",
    initial_num=1100,
    prefix="dataset",
    separator="_",
    suffix="00"
)
```

---

## 📁 项目结构

```
utils_python/
├── script/
│   └── rosbag.py                  # CLI 脚本入口
├── src/
│   └── lovely_utils/
│       ├── ros/
│       │   ├── rosbag_reader.py   # ROS bag读取器
│       │   ├── message_saver.py   # 消息保存器
│       │   └── message_handler.py # 消息处理模块
│       ├── camera_calibration.py  # 相机标定工具
│       ├── video_processor.py     # 视频处理工具
│       └── file_processor.py      # 文件处理工具
├── test/
│   └── ros/
│       ├── util.py
│       ├── test_rosbag_reader.py
│       ├── test_message_saver.py
│       └── test_message_handler.py
├── notebook/
│   ├── calibration_data/         # 标定数据
│   └── get_real_data.py
├── .vscode/
│   └── launch.json
├── .gitignore
├── pyproject.toml
├── setup.py
└── requirements.txt
```

---

## ✅ 测试

使用 `pytest` 进行单元测试：

```bash
pytest
```

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下流程：

1. Fork 仓库
2. 创建分支：`git checkout -b feature/your-feature-name`
3. 提交修改：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature-name`
5. 创建 Pull Request

---

## 📄 许可证

本项目基于 [MIT License](./LICENSE) 开源。