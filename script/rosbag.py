from pathlib import Path
from lovely_utils.ros.rosbag_reader import RosbagReader
from lovely_utils.ros.message_saver import MessageSaver


def extract_msg_from_rosbag():
    bag_path = "/home/ubuntu/Desktop/project/2505_c50b_calibrator/datasets/2025-07-28-office-808-test_RGB_D/2025-07-28-14-35-20.bag"
    path = Path(bag_path)
    topics = ["/topic1", "/topic2"]
    save_dir = "output_dir"
    message_saver = MessageSaver()
    reader = RosbagReader(bag_path, topics, message_saver=message_saver)
    reader.save_msg(save_dir)
    pass


if __name__ == "__main__":
    extract_msg_from_rosbag()
