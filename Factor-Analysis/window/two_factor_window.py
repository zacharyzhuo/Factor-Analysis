import pandas as pd
import numpy as np
import datetime
import requests
import json
from utils.config import Config


class TwoFactorWindow:

    def __init__(self, window_config, report_date, cal, fac):
        self.window_config = window_config
        self._report_date = report_date
        self._cal = cal
        self._fac = fac
        self._n_season = window_config['n_season']
        self._ticker_list = window_config['ticker_list']
        
        self._cfg = Config()
        # 取標的的多少比例
        self._pick_pct = float(self._cfg.get_value('parameter', 'pick_pct'))
    
    def get_ticker_list(self):
        print('[TwoFactorWindow]: get_ticker_list()')
        window_config = self.window_config
        date = self._cal.advance_date(window_config['start_date'], 1, 's')

        factor_list = window_config['factor_list']
        first_factor = factor_list[0]
        second_factor = factor_list[1]

        n_season = self._n_season
        factor_df_dict = {}

        # 抓雙因子的資料
        for factor in factor_list:
            factor_all_date_df = self._fac.factor_df_dict[factor]
            factor_df = factor_all_date_df.loc[date].to_frame()
            # 如果要多看前幾季的因子
            if n_season > 0:
                for i in range(n_season):
                    date = self._cal.advance_date(date, 1, 's')
                    temp_factor_df = factor_all_date_df.loc[date]
                    factor_df = factor_df.join(temp_factor_df)
                # 將這幾季的因子取平均
                factor_df['mean'] = factor_df.mean(axis=1)
                factor_df = factor_df['mean']
            factor_df_dict[factor] = factor_df
        
        # 先以第一個因子排序
        group_list = self._fac.rank_factor(factor_df_dict[first_factor], first_factor)
        # 選籃子
        rank_list = group_list[window_config['group'] - 1]['ticker'].tolist()
        # 抓出這籃子所有標的 第二個因子的資料
        second_factor_df = factor_df_dict[second_factor].loc[rank_list]
        # 用第二個因子資料再排名一次 這個籃子的標的
        group_list = self._fac.rank_factor(second_factor_df, second_factor)
        # 取前幾名
        ticker_list = group_list[0]['ticker'].iloc[0: window_config['position']].tolist()
        self.window_config['ticker_list'] = ticker_list
        self._ticker_list = ticker_list
        # print('ticker_list: ', ticker_list)
        return ticker_list
    
    def _set_t1(self):
        window_config = self.window_config
        factor_list = window_config['factor_list']
        first_factor = factor_list[0]
        second_factor = factor_list[1]
        report_date = self._report_date
        t1_config = {}

        # 3月財報日同時代表著第一季的結束 所以需要多往前數一季
        if report_date.split('-')[1] == '03':
            how = 1
        else:
            how = 0
        date = self._cal.advance_date(report_date, how, 's')

        # 抓雙因子的資料
        factor_df_dict = {}
        for factor in factor_list:
            factor_all_date_df = self._fac.factor_df_dict[factor]
            factor_df = factor_all_date_df.loc[date].to_frame()
            # 抓前幾季的因子資料
            if self._n_season > 0:
                for i in range(self._n_season):
                    date = self._cal.advance_date(date, 1, 's')
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
        window_config = self.window_config
        factor_list = window_config['factor_list']
        first_factor = factor_list[0]
        second_factor = factor_list[1]
        report_date = self._report_date
        first_factor_df = t1_config['first_factor_df']
        second_factor_df = t1_config['second_factor_df']

        # 抓前幾季的這兩個因子資料 並取平均
        if self._n_season > 0:
            first_factor_df['mean'] = first_factor_df.mean(axis=1)
            first_factor_df = first_factor_df['mean']
            second_factor_df['mean'] = second_factor_df.mean(axis=1)
            second_factor_df = second_factor_df['mean']
        
        # 使用這兩個因子都將所有標的排序過 並各自都取固定比例的標的
        ranked_first_factor_df = self._fac.rank_factor(first_factor_df, first_factor, return_list=False)
        how = round(ranked_first_factor_df.shape[0] * self._pick_pct)
        ranked_first_factor_list = ranked_first_factor_df['ticker'].iloc[:how].tolist()
        ranked_second_factor_df = self._fac.rank_factor(second_factor_df, first_factor, return_list=False)
        how = round(ranked_second_factor_df.shape[0] * self._pick_pct)
        ranked_second_factor_list = ranked_second_factor_df['ticker'].iloc[:how].tolist()
        # 取交集
        rank_list = list(set(ranked_first_factor_list) & set(ranked_second_factor_list))

        signal_dict = {}
        # 第一個窗格只能 買 或 繼續空手
        if window_config['if_first'] == True:
            for ticker in self._ticker_list:
                if ticker in rank_list:
                    signal_dict[ticker] = 1
                else:
                    signal_dict[ticker] = 0
            self.window_config['if_first'] = False
        else:
            date = self._cal.get_report_date(report_date, -1)
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
        t2_config['end_date'] = self._cal.get_report_date(report_date, 1)
        # print('t2_config: ', t2_config)
    
    def play_window(self):
        t1_config = self._set_t1()
        self._set_t2(t1_config)
        return self.window_config
