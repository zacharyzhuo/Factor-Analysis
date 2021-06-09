from multiprocessing import Process, freeze_support
from msg.node_msg_handler import NodeMsgHandler
# 忽略警告訊息
import warnings
warnings.filterwarnings("ignore")


# 使用 multiprocessing 必須加上
if __name__ == "__main__":
    freeze_support()
    
    NodeMsgHandler().active_mqtt()
