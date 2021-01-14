import pandas as pd
import numpy as np
import datetime
import requests
import json


class BuyAndHoldWindow:
    def __init__(self, window_config, report_date, cal, fac):
        self.window_config = window_config
        self.report_date = report_date
        self.cal = cal
        self.fac = fac

        t1_config = self._set_t1()
        self._set_t2(t1_config)
    

    def _set_t1(self):
        print('...BuyAndHoldWindow: _set_t1()...')
        window_config = self.window_config
        t1_config = {}
        t1_config['start_date'] = self.cal.get_report_date(self.report_date, -1)
        t1_config['end_date'] = self.report_date
        t1_config['ticker_list'] = self.window_config['ticker_list']
        factor_data = {}
        for factor in window_config['factor_list']:
            fac_dict = {}
            for ticker in t1_config['ticker_list']:
                date = self.cal.advance_date(t1_config['start_date'], 0, 's')
                factor_value = self.fac.factor_df_dict[factor].loc[date, ticker]
                fac_dict[ticker] = factor_value
            factor_data[factor] = fac_dict
        t1_config['factor_data'] = factor_data
        # print('t1_config: ', t1_config)
        return t1_config


    def _set_t2(self, t1_config):
        print('...BuyAndHoldWindow: _set_t2()...')
        window_config = self.window_config
        t2_config = {}
        t2_config['start_date'] = t1_config['end_date']
        t2_config['end_date'] = self.cal.get_report_date(self.report_date, 1)
        ticker_list = t1_config['ticker_list']

        date = t2_config['start_date']
        if date.split("-")[1] == "03":
            how = 1
        else:
            how = 0
        date = self.cal.advance_date(date, how, 's')
        group_list = self.fac.rank_factor(window_config['factor_list'][0], date)
        rank_list = group_list[window_config['group'] - 1]['ticker'].tolist()

        signal_dict = {}
        if window_config['if_first'] == True:
            for ticker in ticker_list:
                if ticker in rank_list:
                    signal_dict[ticker] = 1
                else:
                    signal_dict[ticker] = 0
            self.window_config['if_first'] = False
        else:
            for ticker, signal in window_config['signal'][t1_config['start_date']].items():
                # 0: None; 1: buy; 2: hold; 3: sell
                if signal == 0 and ticker in rank_list:
                    signal_dict[ticker] = 1
                elif signal == 0 and ticker not in rank_list:
                    signal_dict[ticker] = 0
                if signal == 1 and ticker in rank_list:
                    signal_dict[ticker] = 2
                elif signal == 1 and ticker not in rank_list:
                    signal_dict[ticker] = 3
                if signal == 2 and ticker in rank_list:
                    signal_dict[ticker] = 2
                elif signal == 2 and ticker not in rank_list:
                    signal_dict[ticker] = 3
                if signal == 3 and ticker in rank_list:
                    signal_dict[ticker] = 1
                elif signal == 3 and ticker not in rank_list:
                    signal_dict[ticker] = 0
        self.window_config['signal'][t2_config['start_date']] = signal_dict
