import pandas as pd
import numpy as np
import datetime
import requests
import json


class OneFactorWindow:
    def __init__(self, window_config, report_date, cal, fac):
        self.window_config = window_config
        self.report_date = report_date
        self.cal = cal
        self.fac = fac
        self.n_season = window_config['n_season']
    

    def get_ticker_list(self):
        print('...OneFactorWindow: get_ticker_list()...')
        window_config = self.window_config
        date = self.cal.advance_date(window_config['start_date'], 1, 's')
        print('get factor data at ' + date)

        factor = window_config['factor_list'][0]
        n_season = window_config['n_season']
        factor_all_date_df = self.fac.factor_df_dict[factor]
        factor_df = factor_all_date_df.loc[date].to_frame()
        if n_season > 1:
            for i in range(n_season-1):
                date = self.cal.advance_date(date, 1, 's')
                temp_factor_df = factor_all_date_df.loc[date]
                factor_df = factor_df.join(temp_factor_df)
            factor_df['mean'] = factor_df.mean(axis=1)
            factor_df = factor_df['mean']
        group_list = self.fac.rank_factor(factor_df, factor)

        print('get group ' + str(window_config['group']) + ' from ranking list')
        rank_list = group_list[window_config['group'] - 1]
        print('get a ticker list of top ' + str(window_config['position']) + ' from group ' + str(window_config['group']))
        ticker_list = rank_list['ticker'].iloc[0: window_config['position']].tolist()
        return ticker_list
    

    def _set_t1(self):
        print('...OneFactorWindow: _set_t1()...')
        window_config = self.window_config
        n_season = self.n_season
        report_date = self.report_date
        t1_config = {}

        if window_config['if_first'] == True:
            self.window_config['ticker_list'] = self.get_ticker_list()

        if report_date.split('-')[1] == '03':
            how = 1
        else:
            how = 0
        date = self.cal.advance_date(report_date, how, 's')
        factor = window_config['factor_list'][0]
        factor_all_date_df = self.fac.factor_df_dict[factor]
        factor_df = factor_all_date_df.loc[date].to_frame()

        if n_season > 1:
            for i in range(n_season-1):
                date = self.cal.advance_date(date, 1, 's')
                temp_factor_df = factor_all_date_df.loc[date]
                factor_df = factor_df.join(temp_factor_df)

        t1_config['start_date'] = date
        t1_config['end_date'] = report_date
        t1_config['ticker_list'] = window_config['ticker_list']
        t1_config['factor_df'] = factor_df
        # print('t1_config: ', t1_config)
        return t1_config


    def _set_t2(self, t1_config):
        print('...OneFactorWindow: _set_t2()...')
        window_config = self.window_config
        n_season = self.n_season
        report_date = self.report_date
        factor_df = t1_config['factor_df']
        factor = window_config['factor_list'][0]
        ticker_list = t1_config['ticker_list']

        if n_season > 1:
            factor_df['mean'] = factor_df.mean(axis=1)
            factor_df = factor_df['mean']
        group_list = self.fac.rank_factor(factor_df, factor)
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
            date = self.cal.get_report_date(report_date, -1)
            for ticker, signal in window_config['signal'][date].items():
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
        self.window_config['signal'][report_date] = signal_dict
        
        t2_config = {}
        t2_config['start_date'] = t1_config['end_date']
        t2_config['end_date'] = self.cal.get_report_date(report_date, 1)
        # print('t2_config: ', t2_config)
    

    def play_window(self):
        print('...OneFactorWindow: play_window()...')
        t1_config = self._set_t1()
        self._set_t2(t1_config)
        return self.window_config
