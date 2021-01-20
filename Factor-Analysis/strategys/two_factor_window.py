import pandas as pd
import numpy as np
import datetime
import requests
import json


class TwoFactorWindow:
    def __init__(self, window_config, report_date, cal, fac):
        self.window_config = window_config
        self.report_date = report_date
        self.cal = cal
        self.fac = fac
        self.n_season = window_config['n_season']
        self.ticker_list = window_config['ticker_list']
    

    def get_ticker_list(self):
        print('...TwoFactorWindow: get_ticker_list()...')
        window_config = self.window_config
        date = self.cal.advance_date(window_config['start_date'], 1, 's')
        factor_list = window_config['factor_list']
        first_factor = factor_list[0]
        second_factor = factor_list[1]
        n_season = self.n_season
        factor_df_dict = {}

        for factor in factor_list:
            factor_all_date_df = self.fac.factor_df_dict[factor]
            factor_df = factor_all_date_df.loc[date].to_frame()
            if n_season > 0:
                for i in range(n_season):
                    date = self.cal.advance_date(date, 1, 's')
                    temp_factor_df = factor_all_date_df.loc[date]
                    factor_df = factor_df.join(temp_factor_df)
                factor_df['mean'] = factor_df.mean(axis=1)
                factor_df = factor_df['mean']
            factor_df_dict[factor] = factor_df

        group_list = self.fac.rank_factor(factor_df_dict[first_factor], first_factor)
        rank_list = group_list[window_config['group'] - 1]['ticker'].tolist()
        second_factor_df = factor_df_dict[second_factor].loc[rank_list]
        group_list = self.fac.rank_factor(second_factor_df, second_factor)
        ticker_list = group_list[0]['ticker'].iloc[0: window_config['position']].tolist()
        # print('ticker_list: ', ticker_list)
        return ticker_list
    

    def _set_t1(self):
        # print('...TwoFactorWindow: _set_t1()...')
        window_config = self.window_config
        factor_list = window_config['factor_list']
        first_factor = factor_list[0]
        second_factor = factor_list[1]
        report_date = self.report_date
        t1_config = {}

        if window_config['if_first'] == True:
            ticker_list = self.get_ticker_list()
            self.window_config['ticker_list'] = ticker_list
            self.ticker_list = ticker_list

        if report_date.split('-')[1] == '03':
            how = 1
        else:
            how = 0
        date = self.cal.advance_date(report_date, how, 's')

        factor_df_dict = {}
        for factor in factor_list:
            factor_all_date_df = self.fac.factor_df_dict[factor]
            factor_df = factor_all_date_df.loc[date].to_frame()
            if self.n_season > 0:
                for i in range(self.n_season):
                    date = self.cal.advance_date(date, 1, 's')
                    temp_factor_df = factor_all_date_df.loc[date]
                    factor_df = factor_df.join(temp_factor_df)
            factor_df_dict[factor] = factor_df

        t1_config['start_date'] = date
        t1_config['end_date'] = report_date
        t1_config['first_factor_df'] = factor_df_dict[first_factor]
        t1_config['second_factor_df'] = factor_df_dict[second_factor]
        # print('t1_config: ', t1_config)
        return t1_config


    def _set_t2(self, t1_config):
        # print('...TwoFactorWindow: _set_t2()...')
        window_config = self.window_config
        factor_list = window_config['factor_list']
        first_factor = factor_list[0]
        second_factor = factor_list[1]
        report_date = self.report_date
        first_factor_df = t1_config['first_factor_df']
        second_factor_df = t1_config['second_factor_df']
        pick_pct = 0.3 # 取兩個因子排名前幾%的數量

        if self.n_season > 0:
            first_factor_df['mean'] = first_factor_df.mean(axis=1)
            first_factor_df = first_factor_df['mean']
            second_factor_df['mean'] = second_factor_df.mean(axis=1)
            second_factor_df = second_factor_df['mean']
        
        ranked_first_factor_df = self.fac.rank_factor(first_factor_df, first_factor, return_list=False)
        how = round(ranked_first_factor_df.shape[0] * pick_pct)
        ranked_first_factor_list = ranked_first_factor_df['ticker'].iloc[:how].tolist()
        ranked_second_factor_df = self.fac.rank_factor(second_factor_df, first_factor, return_list=False)
        how = round(ranked_second_factor_df.shape[0] * pick_pct)
        ranked_second_factor_list = ranked_second_factor_df['ticker'].iloc[:how].tolist()
        # 取交集
        rank_list = list(set(ranked_first_factor_list) & set(ranked_second_factor_list))

        signal_dict = {}
        if window_config['if_first'] == True:
            for ticker in self.ticker_list:
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
        print('...TwoFactorWindow: play_window()...')
        t1_config = self._set_t1()
        self._set_t2(t1_config)
        return self.window_config
