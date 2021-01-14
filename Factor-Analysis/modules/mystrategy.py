import pandas as pd
import numpy as np
import datetime
import requests
import json

from modules.calendar import Calendar
from modules.factor import Factor
from modules.portfolio import Portfolio


class MyStrategy:
    def __init__(self, strategy_config):
        print('----------------------')
        print('weight_setting: ', strategy_config['weight_setting'])
        print('factor_list: ', strategy_config['factor_list'])
        print('group: ', strategy_config['group'])
        print('position: ', strategy_config['position'])
        print()
        print('start_equity: ', strategy_config['start_equity'])
        print('backtesting period: from ' + strategy_config['start_date'] + ' to ' + strategy_config['end_date'])
        print('----------------------')

        self.strategy_config = strategy_config
        
        self.cal = Calendar('TW')
        self.fac = Factor(strategy_config['factor_list'])
        self.portfolio = None

        ticker_list = self._get_ticker_list()
        self._create_portfolio(ticker_list)
        self._write_portfolio_performance()
        
    
    def _get_ticker_list(self):
        print('...MyStrategy: _get_ticker_list()...')
        strategy_config = self.strategy_config
        date = self.cal.advance_date(strategy_config['start_date'], 1, 's')
        print('get factor data at ' + date)
        group_list = self.fac.rank_factor(strategy_config['factor_list'][0], date)
        print('get group ' + str(strategy_config['group']) + ' from ranking list')
        rank_list = group_list[strategy_config['group'] - 1]
        print('get a ticker list of top ' + str(strategy_config['position']) + ' from group ' + str(strategy_config['group']))
        ticker_list = rank_list['ticker'].iloc[0: strategy_config['position']].tolist()
        print('ticker_list: ', ticker_list)
        return ticker_list
    

    def _create_portfolio(self, ticker_list):
        print('...MyStrategy: _create_portfolio()...')
        self.portfolio = Portfolio(self.strategy_config, ticker_list, self.cal, self.fac)
    

    def _write_portfolio_performance(self):
        print('...MyStrategy: _write_portfolio_performance()...')
        strategy_config = self.strategy_config
        portfo_df = self.portfolio.portfolio_performance_df
        portfo_dict = self.portfolio.portfolio_performance_dict

        file_name = ""
        if strategy_config['weight_setting'] == 0:
            file_name = file_name+"_"+str(strategy_config['weight_setting'])
        file_name = file_name+"_"+strategy_config['factor_list'][0]+"_"+str(strategy_config['group'])+"_"+str(strategy_config['position'])

        path = './portfolio_performance/'+strategy_config['factor_list'][0]+'/'+file_name
        portfo_df.to_csv(path + '.csv', header=True)
        with open(path + '.json', 'w') as file:
            json.dump(portfo_dict, file)
