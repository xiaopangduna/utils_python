import os
import cv2
import json
import yaml
import numpy as np
from cv_bridge import CvBridge

class RosbagReader:
    def __init__(self, bag_path: str):
        self.bag_path = bag_path
        self.generic_saver = GenericSaver()
        
    def read_and_save(self, topics=None, output_dir="."):
        """读取并保存消息"""
        import rosbag
        os.makedirs(output_dir, exist_ok=True)
        
        with rosbag.Bag(self.bag_path, 'r') as bag:
            for topic, msg, t in bag.read_messages(topics=topics):
                try:
                    self.generic_saver.save(msg, topic, t, output_dir)
                except Exception as e:
                    print(f"处理消息失败 [{topic}]: {str(e)}")


class GenericSaver:
    """通用保存器，根据数据类型自动选择保存方式"""
    
    def __init__(self):
        self.bridge = CvBridge()
        self.type_handlers = {}
        self._register_default_handlers()
        
    def _register_default_handlers(self):
        """注册默认的数据类型处理器"""
        # 基本数据类型
        self.register_handler(int)(self._save_scalar)
        self.register_handler(float)(self._save_scalar)
        self.register_handler(str)(self._save_string)
        self.register_handler(bool)(self._save_scalar)
        
        # ROS消息类型（基于内部数据结构）
        self.register_handler(np.ndarray)(self._save_array)
        
        # 特殊ROS消息类型
        try:
            # 尝试导入ROS消息类型（如果环境中存在）
            from sensor_msgs.msg import Image, LaserScan
            self.register_handler(Image)(self._save_image)
            self.register_handler(LaserScan)(self._save_laserscan)
        except ImportError:
            pass  # 如果无法导入ROS消息类型，则不注册相关处理器
        
        # 通用处理（作为后备）
        self.register_handler(object)(self._save_generic)
    
    def register_handler(self, data_type):
        """注册特定数据类型的处理函数（装饰器）"""
        def decorator(func):
            self.type_handlers[data_type] = func
            return func
        return decorator
    
    def save(self, data, topic, timestamp, output_dir):
        """根据数据类型选择合适的处理函数"""
        # 查找最匹配的处理函数（优先使用精确类型，然后是基类）
        handler = None
        for data_type in self.type_handlers:
            if isinstance(data, data_type):
                handler = self.type_handlers[data_type]
                break
        
        if handler:
            filename = self._generate_filename(topic, timestamp)
            full_path = os.path.join(output_dir, filename)
            handler(data, full_path)
            print(f"已保存 {type(data).__name__} 到 {full_path}")
        else:
            raise TypeError(f"无法处理数据类型: {type(data).__name__}")
    
    def _generate_filename(self, topic, timestamp):
        """生成标准化的文件名"""
        base_name = topic.strip("/").replace("/", "_")
        return f"{base_name}_{timestamp.to_sec()}"
    
    # ---------------- 具体类型处理函数 ----------------
    
    def _save_scalar(self, data, path):
        """保存标量数据（int/float/bool）"""
        with open(f"{path}.txt", 'w') as f:
            f.write(str(data))
    
    def _save_string(self, data, path):
        """保存字符串"""
        with open(f"{path}.txt", 'w') as f:
            f.write(data)
    
    def _save_array(self, data, path):
        """保存NumPy数组"""
        np.savetxt(f"{path}.csv", data, delimiter=',')
    
    def _save_image(self, data, path):
        """保存ROS Image消息"""
        cv_img = self.bridge.imgmsg_to_cv2(data, "bgr8")
        cv2.imwrite(f"{path}.jpg", cv_img)
    
    def _save_laserscan(self, data, path):
        """保存LaserScan消息"""
        ranges = np.array(data.ranges)
        angles = np.linspace(data.angle_min, data.angle_max, len(ranges))
        np.savetxt(f"{path}.csv", np.column_stack((angles, ranges)), 
                  delimiter=',', header='angle,range')
    
    def _save_generic(self, data, path):
        """通用处理方式：将对象转为JSON或YAML保存"""
        try:
            # 尝试将对象转换为字典
            if hasattr(data, '__dict__'):
                data_dict = data.__dict__
                with open(f"{path}.json", 'w') as f:
                    json.dump(data_dict, f, indent=2)
            else:
                # 否则使用YAML保存
                with open(f"{path}.yaml", 'w') as f:
                    yaml.dump(str(data), f)
        except Exception as e:
            # 作为最后的手段，保存对象的字符串表示
            with open(f"{path}.txt", 'w') as f:
                f.write(str(data))