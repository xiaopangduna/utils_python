import sys
import pytest

from util_ros.message_saver import MessageSaver
from rosbags.typesys import Stores, get_typestore
from rosbags.typesys.store import Typestore
from util import get_msg_sensor_msgs_msg_Image

def test_save_sensor_msgs_msg_Image():
    msg = get_msg_sensor_msgs_msg_Image()

    pass
def test_register_handler():
    msg = get_msg_sensor_msgs_msg_Image()
    
    pass