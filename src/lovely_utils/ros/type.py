from rosbags.typesys import Stores, get_typestore

ROS_VERSION_MAPPING = {
    "ros1_noetic": Stores.ROS1_NOETIC,
    # "ros2_dashing": Stores.ROS2_DASHING,
    # "ros2_eloquent": Stores.ROS2_ELOQUENT,
    # "ros2_foxy": Stores.ROS2_FOXY,
    # "ros2_galactic": Stores.ROS2_GALACTIC,
    "ros2_humble": Stores.ROS2_HUMBLE,
    # "ros2_iron": Stores.ROS2_IRON,
    # "ros2_jazzy": Stores.ROS2_JAZZY,
    # "ros2_kilted": Stores.ROS2_KILTED,
}