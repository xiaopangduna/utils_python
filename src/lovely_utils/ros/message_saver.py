from .message_handler import *
class MessageSaver:
    """统一消息保存器，支持每次保存时指定输出目录"""
    
    def __init__(self):
        # 初始化时不再需要output_dir参数
        self.handlers = [SensorMsgsMsgImageHandler(), GenericMessageHandler()]
    
    def register_handler(self, handler: MessageHandler):
        """注册新的消息处理器（优先级高于现有处理器）"""
        self.handlers.insert(0, handler)
    
    def save(self, msg, output_dir: str,topic_name: str) -> str:
        """
        保存ROS消息到指定目录
        
        参数:
            msg: ROS消息对象
            topic_name: 话题名称
            output_dir: 保存消息的根目录
            
        返回:
            保存的文件路径，失败时返回None
        """
        # 遍历处理器列表，找到第一个能处理该消息的处理器
        for handler in self.handlers:
            if handler.is_handle(msg):
                return handler.save(msg, output_dir, topic_name)
        
        # 没有找到合适的处理器
        print(f"无可用处理器处理消息: {type(msg).__name__}")
        return None
