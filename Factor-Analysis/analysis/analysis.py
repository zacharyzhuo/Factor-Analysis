import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime
from itertools import product
import matplotlib.pyplot as plt
from utils.config import Config
from utils.general import General
import matplotlib.pyplot as plt


class Analysis:

    def __init__(self):
        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_portfolio_performance')
        self._api_server_IP = self._cfg.get_value('IP', 'api_server_IP')
        self._risk_free_rate = float(self._cfg.get_value('parameter', 'risk_free_rate'))
        self._start_equity = int(self._cfg.get_value('parameter', 'start_equity'))
        self._start_date = self._cfg.get_value('parameter', 'start_date')
        self._end_date = self._cfg.get_value('parameter', 'end_date')

        self._general = General()
    
    def plot_equity_curve(self, request):
        # response = requests.get("http://{}/task/get_task_combi".format(self._api_server_IP), params=request)
        # combination = json.loads(response.text)['result']

        perf_ind_inf_str = ""

        performance_df, equity_df = self._get_request_file(request)
        perf_ind, equity_max = self._compute_performance_ind(equity_df)

        # 計算CAGR MDD MAR並製作顯示字串
        for elm in perf_ind:
            if elm != perf_ind[-1]:
                perf_ind_inf_str = perf_ind_inf_str + "[{}] CAGR: {}, MDD: {}, MAR: {}\n".format(
                    elm[0], elm[1], elm[2], elm[3]
                )
            else:
                perf_ind_inf_str = perf_ind_inf_str + "[{}] CAGR: {}, MDD: {}, MAR: {}".format(
                    elm[0], elm[1], elm[2], elm[3]
                )

        # 日期需設定為index
        ax = equity_df.plot.line(figsize=(12, 8))
        ax.set_xlabel('date')
        ax.set_ylabel('equity')

        # 強調Y軸上某一個點
        ax.axhline(10000000, color='red', linestyle='--')
        # 防止科學符號出現
        ax.ticklabel_format(style='plain', axis='y')

        # 顯示文字註解
        plt.text(
            equity_df.index[0], equity_max/4*3,
            perf_ind_inf_str,
            size=10, ha='left', va='top',
            bbox=dict(
                boxstyle="square", ec=(1., 0.5, 0.5), fc=(1., 0.8, 0.8),
            )
        )

        plt.show()

    def check_cap_util_rate(self, request):
        perf_ind_inf_str = ""

        performance_df, equity_df = self._get_request_file(request)
                
        df = equity_df[[equity_df.columns[0]]].rename({equity_df.columns[0]: 0}, axis=1)
        df.loc[:, :] = np.nan

        position = performance_df['flow'].max()+1
        for i in range(1, position):
            df[i] = df[0]

        for i, row in performance_df.iterrows():
            df.loc[row['start']: row['end'], row['flow']] = 1

        df['cap_util'] = df.iloc[:, :].sum(axis=1)
        df['cap_util_rate'] = df['cap_util'].apply(lambda x: x/position*100)
        df['cap_util_rate'].iloc[-1] = np.nan
        
        equity_df = equity_df.join(df['cap_util_rate'])

        perf_ind, equity_max = self._compute_performance_ind(equity_df.iloc[:, :-1])

        # 計算CAGR MDD MAR並製作顯示字串
        for elm in perf_ind:
            if elm != perf_ind[-1]:
                perf_ind_inf_str = perf_ind_inf_str + "[{}] CAGR: {}, MDD: {}, MAR: {}\n".format(
                    elm[0], elm[1], elm[2], elm[3]
                )
            else:
                perf_ind_inf_str = perf_ind_inf_str + "[{}] CAGR: {}, MDD: {}, MAR: {}".format(
                    elm[0], elm[1], elm[2], elm[3]
                )

        perf_ind_inf_str = perf_ind_inf_str + "\nCapital utilization rate: {}%".format(
            100 - round(df.loc[df['cap_util'] != position].shape[0] / df.shape[0] * 100, 2)
        ) 
        
        # print(df.loc[df['cap_util'] != position])
        # print("total: {}, not full: {}, pct: {}%".format(
        #     df.shape[0], df.loc[df['cap_util'] != position].shape[0],
        #     round(df.loc[df['cap_util'] != position].shape[0] / df.shape[0] * 100, 2)
        # ))
        print(equity_df)
        print(perf_ind)
        print(equity_max)
        print(perf_ind_inf_str)

        ax = equity_df.iloc[:, :-1].plot.line(figsize=(12, 8))

        # 顯示文字註解
        plt.text(
            equity_df.index[-1], 10000000,
            perf_ind_inf_str,
            size=10, ha='right', va='center',
            bbox=dict(
                boxstyle="square", ec=(1., 0.5, 0.5), fc=(1., 0.8, 0.8),
            )
        )

        ax2 = equity_df['cap_util_rate'].plot.line(color='grey', secondary_y=True)
        
        # 強調Y軸上某一個點
        ax.axhline(10000000, color='red', linestyle='--')
        # 防止科學符號出現
        ax.ticklabel_format(style='plain', axis='y')
        
        ax.set_xlabel("Date")
        ax.set_ylabel("Equity")
        ax2.set_ylabel("Capital utilization rate")

        plt.ylim(-10, 110)

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

    def _get_request_file(self, request):
        equity_df = pd.DataFrame()

        # 排列組合參數組合
        data = (
            request['factor_list'],
            request['strategy_list'],
            request['window_list'],
            request['method_list'],
            request['group_list'],
            request['position_list'],
        )
        combination = list(product(*data))

        # 讀檔並串接 equity
        for param in combination:
            performance_df, temp_equity_df = self._read_portfo_perf_file(param)

            if equity_df.empty:
                equity_df = temp_equity_df
            else:
                equity_df = equity_df.join(temp_equity_df)
        
        return performance_df, equity_df

    def _compute_performance_ind(self, df):
        result = []
        equity_max = 0

        for col in df.columns:
            equity_df = df[col]

            # [CAGR]
            start_date_list = self._start_date.split("-")
            end_date_list = self._end_date.split("-")
            final_equity = equity_df.iloc[-1]

            if end_date_list[1] == "1" and end_date_list[2] == "1":
                n = int(end_date_list[0]) - int(start_date_list[0])
            else:
                n = int(end_date_list[0]) - int(start_date_list[0]) + 1

            cagr = ((final_equity / self._start_equity) ** (1/n) - 1) * 100

            # [MDD]
            highest_equity = equity_df.max()
            MDD = 0

            for i, elm in enumerate(equity_df.values.tolist()):
                drawdown = elm - equity_df.iloc[:i].max()

                if drawdown < MDD:
                    MDD = drawdown
                    
            MDD = MDD / highest_equity *100

            MAR = cagr / abs(MDD)

            result.append([col, round(cagr, 1), round(MDD, 1), round(MAR, 3)])

            if equity_df.max() > equity_max:
                equity_max = equity_df.max()
        
        return result, equity_max
        