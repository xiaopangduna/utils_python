import sys
import pytest

from util_ros.message_saver import MessageSaver
from util_ros.message_handler import *
from rosbags.typesys import Stores, get_typestore
from rosbags.typesys.store import Typestore


from util import get_msg_sensor_msgs_msg_Image


def test_SensorMsgsMsgImageHandler_can_handle():
    msg = get_msg_sensor_msgs_msg_Image()

    
    pass

def test_SensorMsgsMsgImageHandler_save():
    msg = get_msg_sensor_msgs_msg_Image()
    
    pass

