from task_allocation.factor_analysis_task_handler import FactorAnalysisTaskHandler
from msg.host_msg_handler import HostMsgHandler


request = {
    "factor_list": [['EPS'], ['GVI'], ['MOM', 'PE'], ['MOM']],
    "strategy_list": [0, 1, 2, 3],
    "group_list": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "position_list": [5, 10, 15, 30, 90, 150],
    "n_season": 0,
}

HostMsgHandler().subscribe_respond()
result = FactorAnalysisTaskHandler(request).schedule_task()

