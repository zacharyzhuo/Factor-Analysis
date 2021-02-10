import os
import pandas as pd
import numpy as np
import datetime
import requests
import json
from modules.portfolio import Portfolio
from utils.config import Config


class MyAsset:

    def __init__(self, strategy_config, cal, fac):
        print('--------------------------------------------')
        print('strategy: ', strategy_config['strategy'])
        print('factor_list: ', strategy_config['factor_list'])
        print('n_season: ', strategy_config['n_season'])
        print('group: ', strategy_config['group'])
        print('position: ', strategy_config['position'])
        print('start_equity: ', strategy_config['start_equity'])
        print('backtesting period: from {} to {}'.format(strategy_config['start_date'], strategy_config['end_date']))
        print('--------------------------------------------')

        self._strategy_config = strategy_config
        self._cal = cal
        self._fac = fac
        
        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_portfolio_performance')

        self._portfolio = None
        self._create_portfolio()
        self._write_portfolio_performance()
    
    def _create_portfolio(self):
        strategy_config = self._strategy_config
        if strategy_config['strategy'] == 0 and len(strategy_config['factor_list']) != 1:
            raise Exception("[ERROR] 單因子策略只能傳入一個因子")
        elif strategy_config['strategy'] == 1 and len(strategy_config['factor_list']) != 2:
            raise Exception("[ERROR] 雙因子策略只能傳入兩個因子")
        elif strategy_config['strategy'] == 2 or strategy_config['strategy'] == 3:
            if len(strategy_config['factor_list']) == 0 or len(strategy_config['factor_list']) > 2:
                raise Exception("[ERROR] 布林通道策略只能傳入一個或兩個因子")

        self._portfolio = Portfolio(strategy_config, self._cal, self._fac)
    
    def _write_portfolio_performance(self):
        strategy_config = self._strategy_config
        portfo_df = self._portfolio.portfolio_performance_df
        portfo_dict = self._portfolio.portfolio_performance_dict

        if len(strategy_config['factor_list']) > 1:
            factor_list_file_name = '&'.join(strategy_config['factor_list'])
        else:
            factor_list_file_name = strategy_config['factor_list'][0]
        path = self._path + factor_list_file_name

        # e.g. 0_MOM_0_1_5 or 1_MOM&GVI_0_1_5
        file_name = "{}_{}_{}_{}_{}".format(
            str(strategy_config['strategy']),
            factor_list_file_name,
            str(strategy_config['n_season']), 
            str(strategy_config['group']), 
            str(strategy_config['position'])
        )

        # 如果沒有這個因子的資料夾就新增一個
        if not os.path.exists(path):
            os.makedirs(path)

        path = "{}/{}".format(path, file_name)
        portfo_df.to_csv(path + '.csv', header=True)
        with open(path + '.json', 'w') as file:
            json.dump(portfo_dict, file)
        print('[MyAsset]: completed writing porfolio performance files')
