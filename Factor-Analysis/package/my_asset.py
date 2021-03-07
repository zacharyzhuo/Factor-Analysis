import os
import pandas as pd
import numpy as np
import datetime
import requests
import json
from package.portfolio import Portfolio
from utils.config import Config
from utils.general import General


class MyAsset:

    def __init__(self, strategy_config, cal, fac):
        print('--------------------------------------------')
        print('factor_list: ', strategy_config['factor_list'])
        print('strategy: ', strategy_config['strategy'])
        print('n_season: ', strategy_config['n_season'])
        print('group: ', strategy_config['group'])
        print('position: ', strategy_config['position'])
        print('start_equity: ', strategy_config['start_equity'])
        print('backtesting period: from {} to {}'.format(
            strategy_config['start_date'], strategy_config['end_date'])
        )
        print('--------------------------------------------')

        self._strategy_config = strategy_config
        self._cal = cal
        self._fac = fac
        
        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_portfolio_performance')
        self._general = General()

        self._portfolio = None
        self._create_portfolio()
        self._write_portfolio_performance()
    
    def _create_portfolio(self):
        print('[MyAsset]: creating protfolio...')

        if self._strategy_config['strategy'] == 0 and \
            len(self._strategy_config['factor_list']) != 1:
            raise Exception("[ERROR] 單因子策略只能傳入一個因子")

        elif self._strategy_config['strategy'] == 1 and \
            len(self._strategy_config['factor_list']) != 2:
            raise Exception("[ERROR] 雙因子策略只能傳入兩個因子")

        elif self._strategy_config['strategy'] == 2:
            if len(self._strategy_config['factor_list']) < 1 or \
                len(self._strategy_config['factor_list']) > 2:
                raise Exception("[ERROR] 布林通道策略只能傳入一個或兩個因子")

        self._portfolio = Portfolio(self._strategy_config, self._cal, self._fac)
    
    def _write_portfolio_performance(self):
        performance_df, equity_df = self._portfolio.get_performance_data()
        factor_str = self._general.factor_to_string(self._strategy_config['factor_list'])
        path = self._path + factor_str

        # e.g. MOM_0_0_1_5 or MOM&GVI_1_0_1_5
        file_name = "{}_{}_{}_{}_{}".format(
            factor_str,
            str(self._strategy_config['strategy']),
            str(self._strategy_config['n_season']), 
            str(self._strategy_config['group']), 
            str(self._strategy_config['position'])
        )

        # 如果沒有這個因子的資料夾就新增一個
        if not os.path.exists(path):
            os.makedirs(path)

        path = "{}/{}".format(path, file_name)
        performance_df.to_csv(path + '.csv', header=True)

        equity_df['date'] = equity_df['date'].dt.strftime('%Y-%m-%d')
        with open(path + '.json', 'w') as file:
            json.dump(equity_df.to_dict(), file)
        print('[MyAsset]: completed writing porfolio performance files')
