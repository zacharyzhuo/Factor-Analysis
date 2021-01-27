import pandas as pd
import numpy as np
import datetime
import requests
import json

from modules.portfolio import Portfolio


class MyAsset:
    def __init__(self, strategy_config, cal, fac):
        print('----------------------')
        print('strategy: ', strategy_config['strategy'])
        print('factor_list: ', strategy_config['factor_list'])
        print('weight_setting: ', strategy_config['weight_setting'])
        print('n_season: ', strategy_config['n_season'])
        print('group: ', strategy_config['group'])
        print('position: ', strategy_config['position'])
        print()
        print('start_equity: ', strategy_config['start_equity'])
        print('backtesting period: from ' + strategy_config['start_date'] + ' to ' + strategy_config['end_date'])
        print('----------------------')

        self.strategy_config = strategy_config
        self.cal = cal
        self.fac = fac

        self.portfolio = None
        self._create_portfolio()
        self._write_portfolio_performance()
    

    def _create_portfolio(self):
        print('...MyAsset: _create_portfolio()...')
        self.portfolio = Portfolio(self.strategy_config, self.cal, self.fac)
    

    def _write_portfolio_performance(self):
        print('...MyAsset: _write_portfolio_performance()...')
        strategy_config = self.strategy_config
        portfo_df = self.portfolio.portfolio_performance_df
        portfo_dict = self.portfolio.portfolio_performance_dict

        if len(strategy_config['factor_list']) > 1:
            factor_list_file_name = '&'.join(strategy_config['factor_list'])
        else:
            factor_list_file_name = strategy_config['factor_list'][0]

        # e.g. 0_MOM_0_1_1_5 or 1_MOM&GVI_0_1_1_5
        file_name = "%s_%s_%s_%s_%s_%s" % (
                                    str(strategy_config['strategy']),
                                    factor_list_file_name, 
                                    str(strategy_config['weight_setting']), 
                                    str(strategy_config['n_season']), 
                                    str(strategy_config['group']), 
                                    str(strategy_config['position']))

        path = './portfolio_performance/'+strategy_config['factor_list'][0]+'/'+file_name
        portfo_df.to_csv(path + '.csv', header=True)
        with open(path + '.json', 'w') as file:
            json.dump(portfo_dict, file)