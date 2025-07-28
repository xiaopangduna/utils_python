import sys
import pytest
import os

from lovely_utils.ros.message_saver import MessageSaver
from rosbags.typesys import Stores, get_typestore
from rosbags.typesys.store import Typestore
from .util import get_msg_sensor_msgs_msg_Image


def test_save_sensor_msgs_msg_Image():
    msg_image = get_msg_sensor_msgs_msg_Image()
    msg_saver = MessageSaver()
    path_img = msg_saver.save(msg_image, "./tmp", "/image")
    assert os.path.exists(path_img)


# def test_register_handler():
#     msg = get_msg_sensor_msgs_msg_Image()

#     pass
