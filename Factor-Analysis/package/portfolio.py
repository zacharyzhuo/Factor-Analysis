import pandas as pd
import numpy as np
import datetime
import requests
import json
import pathos
from multiprocessing import Pool
from backtesting import Backtest, Strategy
from utils.config import Config
from package.window import Window
from utils.plot import Plot


class Portfolio:

    def __init__(self, strategy_config, cal, fac):
        self._strategy_config = strategy_config
        self._cal = cal
        self._fac = fac
        
        self._cfg = Config()

        self._window_config = {
            'strategy': strategy_config['strategy'],
            'factor_list': strategy_config['factor_list'],
            'n_season': strategy_config['n_season'],
            'group': strategy_config['group'],
            'position': strategy_config['position'],
            'start_date': strategy_config['start_date'],
            'end_date': strategy_config['end_date'],
            'cash': strategy_config['start_equity'],
            'if_first': True,
            'performance_df': pd.DataFrame(),
            'equity_df': pd.DataFrame(),
            'heatmap': pd.DataFrame(),
        }
        self._report_date_list = cal.get_report_date_list(
            self._window_config['start_date'], self._window_config['end_date']
        )
        self._slide_window()
        # self._plot_parameter_heatmap()

    def _slide_window(self):
        print('[Portfolio]: running sliding window...')

        # 執行所有窗格運算
        for t2_period in self._get_t2_period(self._report_date_list):
            my_window = Window(
                self._window_config, t2_period, self._cal, self._fac
            )
            # 將本次窗格績效重新賦值
            self._window_config = my_window.window_config
            # break

    def _get_t2_period(self, report_date_list):
        window_period_list = []

        # 窗格數量會比期間內財報公布日數量多一個
        for i in range(len(report_date_list)+1):

            # 第一個窗格T2: 回測期間第一個交易日~第一個財報公布日
            if i == 0:
                date = self._cal.get_trade_date(self._window_config['start_date'], 0, 'd')
                window_period_list.append(
                    [date, report_date_list[i]]
                )

            # 最後一個窗格T2: 最後一個財報公布日~回測期間最後一個交易日
            elif i == len(report_date_list):
                date = self._cal.get_trade_date(self._window_config['end_date'], -1, 'd')
                window_period_list.append(
                    [report_date_list[i-1], date]
                )

            # 其他窗格T2: 兩公布日之間 
            else:
                window_period_list.append(
                    [report_date_list[i-1], report_date_list[i]]
                )

        return window_period_list
    
    def get_performance_data(self):
        return self._window_config['performance_df'], self._window_config['equity_df']

    def _plot_parameter_heatmap(self):
        Plot().plot_heatmap(self._window_config['heatmap'][::-1])
