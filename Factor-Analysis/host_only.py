import time
import pathlib
from multiprocessing import Process, freeze_support
from utils.config import Config
from utils.general import General
from service.calendar import Calendar
from service.factor import Factor
from package.my_asset import MyAsset
import requests
import json


# factor_list = [
#     ['FCF_P', 'CROIC'], ['EV_EBITDA', 'ROIC'], ['FCF_P', 'EPS'], ['EV_EBITDA', 'FCF_OI'],
#     ['FCF_P', 'MOM_7m'], ['EV_S', 'MOM_7m'], ['MOM_52w_PR', 'FCF_P'], ['MOM_52w_PR', 'P_B']
# ]
factor_list = [
    ['GVI']
]
request = {
    "factor_list": factor_list,
    # "strategy_list": [0, 1, 2],
    "strategy_list": [1],
    # "group_list": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "group_list": [1],
    # "position_list": [5, 10, 15, 30, 90, 150],
    "position_list": [5],
    "n_season": 0,
}

# 使用 multiprocessing 必須加上
if __name__ == "__main__":
    freeze_support()
    cfg = Config()
    general = General()

    cal = Calendar('TW')
    get_factor_start = time.time()
    fac = Factor(general.get_distinct_factor_list(factor_list))
    get_factor_end = time.time()
    print("Get factor time: {} second".format(get_factor_end - get_factor_start))


    for g in request['group_list']:
        for p in request['position_list']:
            stra_start = time.time()

            strategy = 2
            n_season = 0

            factor_str = general.factor_to_string(factor_list[0])
            path = cfg.get_value('path', 'path_to_portfolio_performance') + factor_str
            file_name = "{}_{}_{}_{}_{}".format(factor_str, strategy, n_season, g, p)
            file = pathlib.Path("{}/{}.csv".format(path, file_name))

            # if file.exists():
            #     print('file exist!')
            #     break

            # else:
            strategy_config = {
                'factor_list': factor_list[0],
                'strategy': strategy,
                'n_season': n_season,
                'group': g,
                'position': p,
                'start_equity': int(cfg.get_value('parameter', 'start_equity')),
                'start_date': cfg.get_value('parameter', 'start_date'),
                'end_date': cfg.get_value('parameter', 'end_date'),
            }
            my_stra = MyAsset(strategy_config, cal, fac)

            stra_end = time.time()
            print("run strategy time: {} second".format(stra_end - stra_start))

    
    # try:
    #     for task in general.combinate_parameter(
    #         request['factor_list'],
    #         request['strategy_list'],
    #         request['group_list'],
    #         request['position_list']
    #     ):

    #         factor_str = general.factor_to_string(task[0])
    #         path = cfg.get_value('path', 'path_to_portfolio_performance') + factor_str
    #         file_name = "{}_{}_{}_{}_{}".format(factor_str, task[1], request['n_season'], task[2], task[3])
    #         file = pathlib.Path("{}/{}.csv".format(path, file_name))

    #         if file.exists():
    #             print('file exist!')
    #             break

    #         else:
    #             start = time.time()
    #             strategy_config = {
    #                 'factor_list': task[0],
    #                 'strategy': task[1],
    #                 'n_season': request['n_season'],
    #                 'group': task[2],
    #                 'position': task[3],
    #                 'start_equity': int(cfg.get_value('parameter', 'start_equity')),
    #                 'start_date': cfg.get_value('parameter', 'start_date'),
    #                 'end_date': cfg.get_value('parameter', 'end_date'),
    #             }
    #             my_stra = MyAsset(strategy_config, cal, fac)
    #             end = time.time()
    #             print("Execution time: %f second" % (end - start))
    # except Exception as e:
    #     print(e)
       