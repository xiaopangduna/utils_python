import os

from .util import *

from lovely_utils.ros.message_handler import *


def test_SensorMsgsMsgImageHandler_can_handle_is_true(setup_typestore):
    typestore = setup_typestore
    msg_image = get_msg_sensor_msgs_msg_Image(typestore)
    msg_handler = SensorMsgsMsgImageHandler()

    assert msg_handler.can_handle(msg_image) == True


def test_SensorMsgsMsgImageHandler_can_handle_is_false(setup_typestore):
    typestore = setup_typestore
    msg_imu = get_msg_sensor_msgs_msg_Imu(typestore)
    msg_handler = SensorMsgsMsgImageHandler()

    assert msg_handler.can_handle(msg_imu) == False


def test_SensorMsgsMsgImageHandler_save(setup_typestore, setup_temp_dir):
    typestore = setup_typestore
    tmp_dir = setup_temp_dir
    msg_image = get_msg_sensor_msgs_msg_Image(typestore)
    msg_handler = SensorMsgsMsgImageHandler()
    path_img = msg_handler.save(msg_image, tmp_dir, "/image")

    assert os.path.isfile(path_img)


def test_GenericMessageHandler_save_json(setup_typestore, setup_temp_dir):
    typestore = setup_typestore
    tmp_dir = setup_temp_dir
    msg_imu = get_msg_sensor_msgs_msg_Imu(typestore)
    msg_handler = GenericMessageHandler()
    path_imu = msg_handler.save(msg_imu, tmp_dir, "/imu")

    assert os.path.isfile(path_imu)
