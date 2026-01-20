from lovely_utils.ros.rosbag_reader import RosbagReader
from lovely_utils.ros.message_saver import MessageSaver

from .util import *

def test_get_info_dict(setup_typestore, setup_temp_dir):
    # 测试能否正常获取数据
    typestore = setup_typestore
    tmp_dir = setup_temp_dir
    bag_path = tmp_dir / "test.bag"
    topics = ["/camera/color/image_raw"]
    
    # Create a test bag file
    get_ros1_bag_file(
        bag_filename=str(bag_path),
        topics=topics,
        msg_types=["sensor_msgs/msg/Image"],
        typestore=typestore,
    )
    
    # Test the get_info function
    info = RosbagReader._get_info_dict(bag_path, typestore)
    
    # Verify the returned info structure
    assert isinstance(info, dict), "get_info should return a dictionary"
    
    # Check that all expected keys are present
    expected_keys = ['path', 'start_time', 'end_time', 'duration', 'topics', 
                     'total_messages', 'total_topics']
    for key in expected_keys:
        assert key in info, f"Missing expected key: {key}"
    
    # Verify specific values
    assert info['path'] == str(bag_path), "Path should match the bag file path"
    assert info['total_topics'] == 1, "Should have exactly one topic"
    assert info['total_messages'] >= 0, "Should have non-negative message count"
    
    # Check topics structure
    assert isinstance(info['topics'], dict), "Topics should be a dictionary"
    assert len(info['topics']) == 1, "Should have exactly one topic entry"
    
    # Check topic information
    topic_name = topics[0]
    assert topic_name in info['topics'], f"Topic {topic_name} should be in topics info"
    
    topic_info = info['topics'][topic_name]
    expected_topic_keys = ['type', 'count', 'connections', 'message_count']
    for key in expected_topic_keys:
        assert key in topic_info, f"Missing expected topic key: {key}"
    
    assert topic_info['type'] == 'sensor_msgs/msg/Image', "Topic type should match"
    assert topic_info['message_count'] >= 0, "Message count should be non-negative"
    assert topic_info['count'] >= 0, "Count should be non-negative"
    assert topic_info['connections'] >= 0, "Connections count should be non-negative"


def test_save_msg_sensor_msgs_msg_Image(setup_typestore, setup_temp_dir):
    # 测试能否正常获取数据
    typestore = setup_typestore
    tmp_dir = setup_temp_dir
    bag_path = tmp_dir / "test.bag"
    topics = ["/camera/color/image_raw"]
    get_ros1_bag_file(
        bag_filename=str(bag_path),
        topics=topics,
        msg_types=["sensor_msgs/msg/Image"],
        typestore=typestore,
    )
    message_saver = MessageSaver()
    reader = RosbagReader(bag_path, topics, typestore, message_saver)
    reader.save_msg(tmp_dir)
    path_img = tmp_dir / "msg_test"/"camera_color_image_raw" / "1620000000_123456789_sensor_msgs__msg__Image.jpg"
    assert path_img.exists()
    assert os.path.isfile(str(path_img))

# def test_save_msg_sensor_msgs_msg_PointClouds2(setup_typestore, setup_temp_dir):
#     typestore = setup_typestore
#     bag_path = r"/home/ubuntu/Desktop/project/2601_3DLidar_object_detect/datasets/26-01-15-gaoxinhuayuan-lidar/current1_0.bag"
#     topics = [r"/rslidar_points"]
#     message_saver = MessageSaver()
#     reader = RosbagReader(bag_path, topics, typestore, message_saver)
#     reader.save_msg("/home/ubuntu/Desktop/project/utils_python/tmp")
#     pass

# def test_save_msg_sensor_msgs_msg_CameraInfo():
#     bag_path = "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2025-07-24-office-808/2025-07-24-11-16-53.bag"
#     topics = ["/nuwa_1/depth0/camera_info", "/nuwa_1/rgb0/camera_info"]
#     typestore = get_typestore(Stores.ROS1_NOETIC)
#     message_saver = MessageSaver()
#     reader = RosbagReader(bag_path, topics, typestore, message_saver)
#     reader.save_msg("/home/ubuntu/Desktop/project/utils_python/tmp")


# def test_save_sensor_msgs_msg_Image_and_CameraInfo():
#     bag_path = "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2025-07-28-office-808-test_RGB_D/2025-07-28-14-35-20.bag"
#     topics = [
#         "/nuwa_1/rgb0/image",
#         "/nuwa_1/rgb0/camera_info",
#     ]
#     typestore = get_typestore(Stores.ROS1_NOETIC)
#     message_saver = MessageSaver()
#     reader = RosbagReader(bag_path, topics, typestore, message_saver)
#     reader.save_msg("/home/ubuntu/Desktop/project/utils_python/tmp")
