from .util import *

from lovely_utils.ros.message_saver import *


def test_get_handler_is_sensor_msgs_msg_Image(setup_typestore):
    typestore = setup_typestore
    msg_image = get_msg_sensor_msgs_msg_Image(typestore)
    msg_saver = MessageSaver()
    handler = msg_saver.get_handler(msg_image)
    assert isinstance(handler, SensorMsgsMsgImageHandler)

