from __future__ import annotations

from cv2.gapi.wip.draw import Image
import numpy as np

from rosbags.rosbag1 import Writer
from rosbags.typesys import Stores, get_typestore
from rosbags.typesys.stores.ros1_noetic import (
    builtin_interfaces__msg__Time as Time,
    sensor_msgs__msg__CompressedImage as CompressedImage,
    sensor_msgs__msg__Image as ImageMsg,
    std_msgs__msg__Header as Header,
)
from pathlib import Path

TOPIC = '/camera'
FRAMEID = 'map'
IMAGES = []
# Contains filenames and their timestamps
dir_imgs = Path("/home/ubuntu/Desktop/project/2025-08-12/exp12")
imgs = []
for path in dir_imgs.iterdir():
    if path.is_file():
        imgs.append(path)
imgs.sort(key=lambda x: x.stem.split('_')[-1])
for idx, img in enumerate(imgs):
    IMAGES.append((str(img), idx))
#     print(img.stem)
# IMAGES = [('homer.jpg', 42), ('marge.jpg', 43)]


def save_images() -> None:
    """Iterate over IMAGES and save to output bag."""
    typestore = get_typestore(Stores.ROS1_NOETIC)
    with Writer('output1.bag') as writer:
        conn = writer.add_connection(TOPIC, ImageMsg.__msgtype__, typestore=typestore)

        for idx, (path, seq) in enumerate(IMAGES):
            timestamp = int(Path(path).stem.split('_')[-1])
            msg = ImageMsg(
                Header(
                    seq=seq,
                    stamp=Time(sec=int(timestamp // 10**9), nanosec=int(timestamp % 10**9)),
                    frame_id=FRAMEID,
                ),
                height=480,
                width=640,
                encoding='bgr8',
                is_bigendian=False,
                step=640* 3,
                data=np.fromfile(path, dtype=np.uint8),
            )

            writer.write(
                conn,
                timestamp,
                typestore.serialize_ros1(msg, ImageMsg.__msgtype__),
            )


if __name__ == '__main__':
    save_images()