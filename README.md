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

项目使用 [uv](https://docs.astral.sh/uv/) 管理 Python 版本、虚拟环境和依赖。需要 Python 3.12 或更高版本。

```bash
# 安装 uv：https://docs.astral.sh/uv/getting-started/installation/
uv sync
```

`uv sync` 会按 `uv.lock` 创建 `.venv` 并安装本包及依赖。之后用 `uv run` 运行命令，例如：

```bash
uv run lovely_utils --help
uv run pytest test/
```

---

## 🚀 使用方法

### 命令行接口（CLI）

安装后可直接通过 `lovely_utils` 命令使用。

#### 查看 ROS Bag 信息

```bash
lovely_utils rosbag info \
  --bag-paths /path/to/your.bag \
  --bag-paths /path/to/your.bag \
  --bag-folders /path/to/your_bag_folder \
  --typestore ros1_noetic
```

#### 提取 ROS Bag 消息

```bash
lovely_utils rosbag save \
  --bag-paths /path/to/your.bag \
  --bag-paths /path/to/your.bag \
  --bag-folders /path/to/your_bag_folder \
  --topics /camera/image_raw \
  --topics /camera/camera_info \
  --save-dir ./output
```

#### 生成 标定板 图案

```bash
lovely_utils camera calibration generate-board aruco-gridboard save \
  --dictionary DICT_6X6_250 \
  --cols 5 \
  --rows 7 \
  --marker-length-mm 30 \
  --marker-sep-mm 6 \
  --start-id 0 \
  --out-dir ./output \
  --margin-mm 10 \
  --dpi 127
```

```bash
lovely_utils camera calibration generate-board charuco-board save \
  --dictionary DICT_6X6_250 \
  --cols 4 \
  --rows 3 \
  --square-length-mm 20 \
  --marker-length-mm 12 \
  --out-dir ./output \
  --dpi 300
```

```bash
lovely_utils camera calibration generate-board april-board save \
  --dictionary t36h11 \
  --cols 6 \
  --rows 6 \
  --marker-length-mm 80 \
  --marker-sep-mm 24 \
  --start-id 0 \
  --rotation 2 \
  --symm-corners \
  --out-dir ./output
```

> 提示：PNG 在不同打印软件中物理尺寸可能不易控制，**推荐使用 PDF 输出**，以获得更稳定的标定板实际尺寸。

#### 从视频抽帧

`--video` 可重复。传入文件就处理该文件；传入文件夹只扫这一层常见视频后缀，不进入子目录。每个视频的帧写到 `{save-dir}/{视频名}/`，文件名默认是 `{视频名}_{帧号}.jpg`。传入 `--prefix` 时改为 `{prefix}_{帧号}.jpg`。同一批里视频同名时，后一个目录为 `{视频名}_2`、`{视频名}_3`。解码遇到损坏的数据包时会跳过并继续；`--freq 1` 时，结果里会标出容器帧数和未能解码的帧数。

```bash
lovely_utils video extract-frames \
  --video /path/to/video.mp4 \
  --video /path/to/another.mp4 \
  --video /path/to/video_folder \
  --save-dir ./frames \
  --freq 5
```

---

### Python 脚本调用

#### 提取 ROS Bag 消息--script/rosbag.py

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
│       ├── video/
│       │   ├── video_processor.py # 视频处理工具
│       │   └── cli.py             # 视频命令行
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
├── uv.lock
└── requirements.txt
```

---

## ✅ 测试

使用 `pytest` 进行单元测试：

```bash
uv run pytest test/
```

## 🤝 贡献指南

欢迎贡献代码！请遵循以下流程：

1. Fork 仓库
2. 创建分支：`git checkout -b feature/your-feature-name`
3. 提交修改：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature-name`
5. 创建 Pull Request

---

png打印无法控制标定板的物理大小，用pdf更合适
## 📄 许可证

本项目基于 [MIT License](./LICENSE) 开源。