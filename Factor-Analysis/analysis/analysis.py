import os
import pandas as pd
import json
import matplotlib.pyplot as plt
from multiprocessing.dummy import Pool as ThreadPool
import pathos
from multiprocessing import Pool
from utils.config import Config
from utils.general import General
from utils.plot import Plot


class Analysis:

    def __init__(self):
        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_portfolio_performance')

        self._general = General()
        self._plot = Plot()

        self.factor_stirng = ""
        self.performance_df = pd.DataFrame()
        self.equity_df = pd.DataFrame()
    
    def analysis(self, request):
        para_list = [
            request['factor_list'], request['strategy_list'][0],
            request['group_list'][0], request['position_list'][0],
        ]
        self._read_portfo_perf_file(para_list)
        self._plot_equity_curve()

    def _read_portfo_perf_file(self, para_list):

        # 將[fac1, fac2] 轉成 fac1&fac2
        factor_str = self._general.factor_to_string(para_list[0])
        path = "{}{}/".format(self._path, factor_str)
        file_name = "{}_{}_{}_{}_{}".format(
            factor_str,
            para_list[1],
            str(0), 
            str(para_list[2]), 
            str(para_list[3])
        )

        self.performance_df = pd.read_csv("{}{}.csv".format(path, file_name)).drop('Unnamed: 0', axis=1)

        with open(path+file_name+'.json', 'r') as file:
            json_data = json.load(file)
        self.equity_df = pd.DataFrame.from_dict(json_data)
        self.equity_df['date']= pd.to_datetime(self.equity_df['date'])
        self.equity_df = self.equity_df.set_index('date')

        print("read {}".format(file_name))
        # return {
        #     'file_name': file_name,
        #     'strategy': para_list[1],
        #     'performance_df': performance_df,
        #     'equity_df': equity_df,
        # }

    def _plot_equity_curve(self):
        print(self.equity_df)
        print(self.performance_df.sort_values(by=['return'], ascending=False))
        self._plot.plot_line_chart(self.equity_df, 'date', 'equity')

