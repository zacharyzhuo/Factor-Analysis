import pandas as pd
import numpy as np
import datetime
import requests
import json


# portfolio_config = {
#     'ticker_list': ['1101'],
#     'factor_list': ['MOM'],
#     'n_season': 1,
#     'group': 1,
#     'position': 5,
#     'start_date': '2010-01-01',
#     'end_date': '2017-12-31',
# }

class BuyAndHoldWindow:
    def __init__(self, portfolio_config, report_date, cal, fac):
        self.portfolio_config = portfolio_config
        self.report_date = report_date
        self.cal = cal
        self.fac = fac
        t1_config = self._set_t1()
        self._set_t2(t1_config)
    
    def _set_t1(self):
        portfolio_config = self.portfolio_config
        t1_config = {}
        t1_config['start_date'] = self.cal.get_report_date(self.report_date, -1)
        t1_config['end_date'] = self.report_date
        t1_config['ticker_list'] = self.portfolio_config['ticker_list']

        if portfolio_config['if_first'] == True:
            signal_dict = {}
            for ticker in t1_config['ticker_list']:
                signal_dict[ticker] = 0
            t1_config['signal'] = signal_dict
        # else:

        print(t1_config)
        return t1_config

    def _set_t2(self, t1_config):
        portfolio_config = self.portfolio_config
        t2_config = {}
        t2_config['start_date'] = t1_config['end_date']
        t2_config['end_date'] = self.cal.get_report_date(self.report_date, 1)
        ticker_list = t1_config['ticker_list']

        group_list = self.fac.rank_factor(portfolio_config['factor_list'][0], t2_config['start_date'])
        rank_list = group_list[portfolio_config['group'] - 1]['ticker'].tolist()

        # print(rank_list)
        print(t2_config)
