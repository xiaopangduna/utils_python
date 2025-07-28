import sys
import pytest
import os

from rosbags.typesys import Stores, get_typestore
from rosbags.typesys.store import Typestore

from lovely_utils.ros.message_handler import SensorMsgsMsgImageHandler

from .util import get_msg_sensor_msgs_msg_Image


def test_SensorMsgsMsgImageHandler_is_handle():
    msg_image = get_msg_sensor_msgs_msg_Image()
    msg_handler = SensorMsgsMsgImageHandler()

    assert msg_handler.is_handle(msg_image)


def test_SensorMsgsMsgImageHandler_save():
    msg_image = get_msg_sensor_msgs_msg_Image()
    msg_handler = SensorMsgsMsgImageHandler()
    path_img = msg_handler.save(msg_image, "./tmp", "/image")

    # 检查文件是否存在
    assert os.path.exists(path_img)
