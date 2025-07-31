from pathlib import Path
from rosbags.typesys import Stores, get_typestore
from lovely_utils.ros.rosbag_reader import RosbagReader
from lovely_utils.ros.message_saver import MessageSaver


def extract_msg_from_rosbag():
    path_bag = "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2025-07-28-office-808-test_RGB_D/2025-07-28-14-35-20.bag"
    path_bag = Path(path_bag)
    topics = ["/topic1", "/topic2"]
    save_dir = "output_dir"
    message_saver = MessageSaver()
    ros_version = Stores.ROS1_NOETIC if "bag" in path_bag.suffix else Stores.ROS2_HUMBLE
    typestore = get_typestore(ros_version)
    reader = RosbagReader(path_bag, topics, typestore=typestore, message_saver=message_saver)
    reader.save_msg(save_dir)



def get_rosbag_info():
    path_bag = "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2025-07-28-office-808-test_RGB_D/2025-07-28-14-35-20.bag"
    path_bag = Path(path_bag)
    ros_version = Stores.ROS1_NOETIC if "bag" in path_bag.suffix else Stores.ROS2_HUMBLE
    typestore = get_typestore(ros_version)
    info = RosbagReader.get_info(path_bag, typestore=typestore)
    print(info)


if __name__ == "__main__":
    get_rosbag_info()
    extract_msg_from_rosbag()

