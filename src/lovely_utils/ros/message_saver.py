from .message_handler import *

class MessageSaver:
    """统一消息保存器，支持每次保存时指定输出目录"""

    def __init__(self):
        self.handlers = [SensorMsgsMsgImageHandler(), SensorMsgsMsgPointCloud2Handler(), GenericMessageHandler()]

    def register_handler(self, handler: MessageHandler):
        """注册新的消息处理器（优先级高于现有处理器）"""
        self.handlers.insert(0, handler)

    def get_handler(self, msg) -> MessageHandler:
        """
        获取适合的消息处理器

        参数:
            msg: ROS消息对象

        返回:
            适合的处理器，若无合适处理器返回 None
        """
        for handler in self.handlers:
            if handler.can_handle(msg):
                return handler
        print(f"无可用处理器处理消息: {type(msg).__name__}")
        return None