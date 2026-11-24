import importlib

import typer

app = typer.Typer()

# video 必须能独立启动。rosbag / camera 依赖未安装时只跳过对应命令。
_COMMAND_GROUPS = (
    ("lovely_utils.ros.rosbag_reader_cli", "rosbag", True),
    ("lovely_utils.camera.cli", "camera", True),
    ("lovely_utils.video.cli", "video", False),
)

for module_name, command_name, optional in _COMMAND_GROUPS:
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        if not optional:
            raise
        continue
    app.add_typer(module.app, name=command_name)


def main():
    app()


if __name__ == "__main__":
    main()
