import time
from multiprocessing import Process, freeze_support
from task_allocation.factor_analysis_task_handler import FactorAnalysisTaskHandler
from msg.host_msg_handler import HostMsgHandler


factor_list = [
    # ['EV_EBITDA', 'ROIC'], ['P_B', 'EPS'], ['FCF_P', 'MOM'],
    # ['FCF_OI', 'P_S'], ['FCF_P'], ['EV_EBITDA'],
    # ['P_B'], ['P_S'], ['MOM'],
    # ['EPS'], ['ROIC'], ['FCF_OI']

    ['EV_EBITDA']
]
request = {
    "factor_list": factor_list,
    "strategy_list": [1],
    "window_list": [2],
    "method_list": [0, 1],
    "group_list": [1, 2, 3, 4, 5],
    "position_list": [6, 15, 60, 150, 300],
}


# 使用 multiprocessing 必須加上
if __name__ == "__main__":
    freeze_support()

    start = time.time()
    
    HostMsgHandler().active_mqtt()
    result = FactorAnalysisTaskHandler(request).schedule_task()

    end = time.time()
    print("total time: {} second".format(end - start))

