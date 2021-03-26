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
        self._strategy_config = strategy_config
        self._cal = cal
        self._fac = fac
        
        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_portfolio_performance')
        self._general = General()

        self._factor_str = self._general.factor_to_string(self._strategy_config['factor_list'])
        self._portfolio = None

        self._show_task_detail()
        self._create_portfolio()
        self._write_portfolio_performance()
    
    def _show_task_detail(self):
        columns_list = [
            'factor_list', 'strategy', 'n_season', 'group', 
            'position', 'start_equity', 'period'
        ]

        df = pd.DataFrame().append({
            'factor_list': self._factor_str, 'strategy': self._strategy_config['strategy'], 
            'n_season': self._strategy_config['n_season'], 'group': self._strategy_config['group'], 
            'position': self._strategy_config['position'], 'start_equity': self._strategy_config['start_equity'], 
            'period': "from {} to {}".format(self._strategy_config['start_date'], self._strategy_config['end_date'])
        }, ignore_index=True)[columns_list]

        print(df.set_index('factor_list').T)
    
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
        performance_df = performance_df[['ticker', 'start', 'end', 'start_equity', 'final_equity', 'return']]
        path = self._path + self._factor_str

        # e.g. MOM_0_0_1_5 or MOM&GVI_1_0_1_5
        file_name = "{}_{}_{}_{}_{}".format(
            self._factor_str,
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
