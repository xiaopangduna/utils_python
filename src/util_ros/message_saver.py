from .message_handler import MessageHandler, GenericMessageHandler, SensorMsgsMsgImageHandler
class MessageSaver:
    """统一消息保存器"""
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.handlers = [SensorMsgsMsgImageHandler(), GenericMessageHandler()]
    
    def register_handler(self, handler: MessageHandler):
        self.handlers.insert(0, handler)  # 新处理器优先
    
    def save_message(self, msg, topic_name: str) -> str:
        for handler in self.handlers:
            if handler.can_handle(msg):
                return handler.save(msg, self.output_dir, topic_name)
        print(f"无可用处理器处理消息: {type(msg).__name__}")
        return None
