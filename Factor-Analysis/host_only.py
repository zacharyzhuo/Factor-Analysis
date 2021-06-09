import time
import pathlib
import requests
import json
from multiprocessing import Process, freeze_support
from utils.config import Config
from utils.general import General
from service.calendar import Calendar
from service.factor import Factor
from package.my_asset import MyAsset
from itertools import product
# 忽略警告訊息
import warnings
warnings.filterwarnings("ignore")


factor_list = [
    # ['FCF_P', 'CROIC'], ['EV_EBITDA', 'ROIC'], ['P_B', 'EP'], ['ROE', 'P_B'],
    # ['ROIC', 'P_S'], ['CROIC', 'P_IC'], ['FCFPS', 'EV_EBITDA'], ['FCF_P', 'EPS'],
    # ['P_B', 'EPS'], ['FCF_P', 'MOM_7m'], ['EV_S', 'MOM_7m'], ['MOM_52w_PR', 'FCF_P'],
    # ['MOM_52w_PR', 'P_B'], ['EV_EBITDA', 'FCF_OI'], ['FCF_OI', 'P_S'], ['P_B', 'OCF_E']
]
factor_list = [
    ['EV_EBITDA', 'ROIC'], ['P_B', 'EPS'], ['FCF_P', 'MOM'],
    # ['FCF_OI', 'P_S'], ['FCF_P'], ['EV_EBITDA'],
    # ['P_B'], ['P_S'], ['MOM'],
    # ['EPS'], ['ROIC'], ['FCF_OI']
]
factor_list = [
    # ['FCF_P'],
    ['EV_EBITDA'],
]
request = {
    "factor_list": factor_list,
    "strategy_list": [1],
    "window_list": [0],
    "method_list": [1],
    # "group_list": [1, 2, 3],
    # "position_list": [6, 15, 60, 150, 300],
    "group_list": [1],
    "position_list": [6, 15, 60],
}

# 使用 multiprocessing 必須加上
if __name__ == "__main__":
    freeze_support()

    general = General()
    cfg = Config()
    cal = Calendar('TW')
    fac = Factor(general.get_distinct_factor_list(factor_list))

    api_server_IP = cfg.get_value('IP', 'api_server_IP')

    request["factor_list"] = general.factor_list_to_string(request["factor_list"])
    response = requests.get("http://{}/task/get_task_combi".format(api_server_IP), params=request)
    combination = json.loads(response.text)['result']
    print(combination)

    try:

        for task in combination:
            factor_str = general.factor_to_string(task[0])
            path = cfg.get_value('path', 'path_to_portfolio_performance') + factor_str
            file_name = "{}_{}_{}_{}_{}_{}".format(
                factor_str,
                task[1],
                task[2],
                task[3],
                task[4],
                task[5],
            )
            file = pathlib.Path("{}/{}.csv".format(path, file_name))

            if file.exists():
                print('file exist!')
                continue

            else:

                start = time.time()
                strategy_config = {
                    'factor': task[0],
                    'strategy': task[1],
                    'window': task[2],
                    'method': task[3],
                    'group': task[4],
                    'position': task[5],
                }
                my_stra = MyAsset(strategy_config, cal, fac)
                end = time.time()
                print("Execution time: %f second" % (end - start))

    except Exception as e:
        print(e)
       