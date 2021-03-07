import time
from multiprocessing import Process, freeze_support
from task_allocation.factor_analysis_task_handler import FactorAnalysisTaskHandler
from msg.host_msg_handler import HostMsgHandler

# factor_list = [
#     ['FCF_P', 'CROIC'], ['EV_EBITDA', 'ROIC'], ['P_B', 'EP'], ['ROE', 'P_B'],
#     ['ROIC', 'P_S'], ['CROIC', 'P_IC'], ['FCFPS', 'EV_EBITDA'], ['FCF_P', 'EPS'],
#     ['P_B', 'EPS'], ['FCF_P', 'MOM_7m'], ['EV_S', 'MOM_7m'], ['MOM_52w_PR', 'FCF_P'],
#     ['MOM_52w_PR', 'P_B'], ['EV_EBITDA', 'FCF_OI'], ['FCF_OI', 'P_S'], ['P_B', 'OCF_E']
# ]
factor_list = [
    # ['GVI']
    ['EPS'], ['MOM_7m'], ['MOM_52w_PR'], ['PE'], ['EV_EBITDA'],
    ['EV_S'], ['FCF_P'], ['CROIC'], ['FCF_OI'], ['FCF_LTD'],
    ['ROE'], ['ROIC'], ['P_B'], ['EP'], ['P_S'],
    ['P_IC'], ['OCF_E'], ['FCFPS']
]
request = {
    "factor_list": factor_list,
    "strategy_list": [0, 1, 2],
    "group_list": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "position_list": [5, 10, 15, 30, 90, 150],
    "n_season": 0,
}


# 使用 multiprocessing 必須加上
if __name__ == "__main__":
    freeze_support()

    start = time.time()
    
    HostMsgHandler().active_mqtt()
    result = FactorAnalysisTaskHandler(request).schedule_task()

    end = time.time()
    print("total time: {} second".format(end - start))

