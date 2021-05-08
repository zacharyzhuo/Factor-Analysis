import os
import pandas as pd
import numpy as np
import requests
import json
import pathos
from datetime import datetime
from itertools import product
import matplotlib.pyplot as plt
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool
from utils.config import Config
from utils.general import General
from utils.plot import Plot
import matplotlib.pyplot as plt


class Analysis:

    def __init__(self):
        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_portfolio_performance')
        self._api_server_IP = self._cfg.get_value('IP', 'api_server_IP')

        self._general = General()
        self._plot = Plot()

        # self.performance_df = pd.DataFrame()
    
    def plot_equity_curve(self, request):
        equity_df = pd.DataFrame()

        # response = requests.get("http://{}/task/get_task_combi".format(self._api_server_IP), params=request)
        # combination = json.loads(response.text)['result']

        data = (
            request['factor_list'],
            request['strategy_list'],
            request['window_list'],
            request['method_list'],
            request['group_list'],
            request['position_list'],
        )
        combination = list(product(*data))

        for param in combination:
            performance_df, temp_equity_df = self._read_portfo_perf_file(param)

            if equity_df.empty:
                equity_df = temp_equity_df
            else:
                equity_df = equity_df.join(temp_equity_df)

        # print(self.performance_df.sort_values(by=['return'], ascending=False))
        self._plot.plot_line_chart(equity_df, 'date', 'equity')

    def check_cap_util_rate(self, request):
        equity_df = pd.DataFrame()
        data = (
            request['factor_list'],
            request['strategy_list'],
            request['window_list'],
            request['method_list'],
            request['group_list'],
            request['position_list'],
        )
        combination = list(product(*data))
        print(combination)
        for param in combination:
            performance_df, temp_equity_df = self._read_portfo_perf_file(param)
            print(temp_equity_df)

            if equity_df.empty:
                equity_df = temp_equity_df
            else:
                equity_df = equity_df.join(temp_equity_df)
            # if param[1] == 0:
                
        df = equity_df[[equity_df.columns[0]]].rename({equity_df.columns[0]: 0}, axis=1)
        df.loc[:, :] = np.nan

        position = performance_df['flow'].max()+1
        for i in range(1, position):
            df[i] = df[0]

        for i, row in performance_df.iterrows():
            df.loc[row['start']: row['end'], row['flow']] = 1

        df['cap_util'] = df.iloc[:, :].sum(axis=1)
        df['cap_util_rate'] = df['cap_util'].apply(lambda x: x/position*100)
        
        equity_df = equity_df.join(df['cap_util_rate'])
        print(equity_df)

        # ax = equity_df[, :-1].plot.line()
        ax = equity_df.iloc[:, :-1].plot.line(figsize=(12, 8))
        equity_df['cap_util_rate'].plot(kind='line', color='grey', secondary_y=True)
        # 防止科學符號出現
        ax.ticklabel_format(style='plain', axis='y')
        
        ax.set_xlabel("date")
        ax.set_ylabel("equity")

        plt.show()

    def _read_portfo_perf_file(self, param):
        # 將[fac1, fac2] 轉成 fac1&fac2
        factor_str = self._general.factor_to_string(param[0])
        path = "{}{}/".format(self._path, factor_str)
        file_name = "{}_{}_{}_{}_{}_{}".format(
            factor_str,
            param[1], # strategy
            param[2], # window
            param[3], # method
            param[4], # group
            param[5], # position
        )

        performance_df = pd.read_csv("{}{}.csv".format(path, file_name)).drop('Unnamed: 0', axis=1)

        with open(path+file_name+'.json', 'r') as file:
            json_data = json.load(file)
        equity_df = pd.DataFrame.from_dict(json_data)
        equity_df['date']= pd.to_datetime(equity_df['date'])
        equity_df = equity_df.set_index('date')
        equity_df.columns = [file_name]

        print("read {}".format(file_name))
        return performance_df, equity_df
        

