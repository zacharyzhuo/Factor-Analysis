import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from utils.config import Config
from utils.general import General
from service.calendar import Calendar


COLOR = [
    'red', 'orange', 'yellow', 'green',
    'skyblue', 'blue', 'purple', 'black',
    'grey', 'pink', 'lime',  'brown',
]


class Analysis:

    def __init__(self):
        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_portfolio_performance')
        self._api_server_IP = self._cfg.get_value('IP', 'api_server_IP')
        self._start_equity = int(self._cfg.get_value('parameter', 'start_equity'))
        self._start_date = self._cfg.get_value('parameter', 'start_date')
        self._end_date = self._cfg.get_value('parameter', 'end_date')

        self._general = General()
        self._cal = Calendar('TW')
    
    def plot_equity_curve(self, request):
        perf_ind_inf_str = ""

        equity_df, performance_df = self._read_request_files(request)
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

        equity_df, performance_df = self._read_request_files(request)
 
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

    def plot_performance_heatmap(self, request):
        heatmap_df = pd.DataFrame(columns=[6, 15, 60, 150, 300])
        strategy_str = ''

        if request['strategy'] == 0:
            strategy_str = 'Buy and Hold'
        elif request['strategy'] == 1:
            strategy_str = 'BBands'

        df = self.query_performance_file()
        df = df.loc[
            (df['factor'] == request['factor']) &
            (df['strategy'] == request['strategy']) &
            (df['method'] == request['method'])
        ]

        for i in [1, 2, 3, 4, 5]:
            cagr_list = []

            for col in heatmap_df.columns:
                cagr_list.append(
                    df[request['perf_ind']].loc[
                        (df['group']==i) & (df['position']==col)
                    ].values[0]
                )
            
            heatmap_df.loc[i] = cagr_list

        print(heatmap_df)

        ax = sns.heatmap(heatmap_df, cmap="YlGnBu")

        ax.set_xlabel("Position")
        ax.set_ylabel("Group")

        ax.set_title("[{}] {} / {}".format(
            request['perf_ind'], request['factor'], strategy_str)
        )

        plt.show()

    def plot_profit_bar_chart(self, request):
        file_name = "{}_{}_{}_{}_{}_{}".format(
            request['factor'],
            request['strategy'],
            request['window'],
            request['method'],
            request['group'],
            request['position'],
        )
        trade_df = pd.read_csv('{}{}/{}.csv'.format(
            self._path, request['factor'], file_name
        )).drop('Unnamed: 0', axis=1)
        print(trade_df)

        report_date_list = self._cal.get_report_date_list(self._start_date, self._end_date)
        print(report_date_list)

        window_period_list = []

        # 窗格數量會比期間內財報公布日數量多一個
        for i in range(len(report_date_list)+1):

            # 第一個窗格T2: 回測期間第一個交易日~第一個財報公布日
            if i == 0:
                date = self._cal.get_trade_date(self._start_date, 0, 'd')
                window_period_list.append(
                    [date, report_date_list[i]]
                )

            # 最後一個窗格T2: 最後一個財報公布日~回測期間最後一個交易日
            elif i == len(report_date_list):
                date = self._cal.get_trade_date(self._end_date, -1, 'd')
                window_period_list.append(
                    [report_date_list[i-1], date]
                )

            # 其他窗格T2: 兩公布日之間 
            else:
                window_period_list.append(
                    [report_date_list[i-1], report_date_list[i]]
                )
        
        print(window_period_list)

        # print(trade_df.sort_values(by=['return'], ascending=False))

        trade_df.plot.bar(y='return', figsize=(20, 8))
        plt.show()
    
    def plot_linear_regression(self, request):
        df = self.query_performance_file()
        factor_str_list = []

        fig = plt.figure(figsize=(15, 10))

        for i, factor in enumerate(request['factor_list']):
            factor_str = self._general.factor_to_string(factor)
            factor_str_list.append(factor_str)

            temp_df = df.loc[
                (df['factor'] == factor_str) &
                (df['strategy'] == request['strategy']) &
                (df['window'] == request['window']) &
                (df['method'] == request['method']) &
                (df['position'] == request['position'])
            ]

            ax = sns.regplot(x=temp_df['group'], y=temp_df[request['perf_ind']], color=COLOR[i])
            ax.set(xticks=range(1, len(temp_df['group'])+1, 1))

        plt.legend(labels=factor_str_list)
        plt.title('[{}] {}_{}_{}_{}'.format(
            request['perf_ind'], request['strategy'],
            request['window'], request['method'],
            request['position']
        ), size=24)
        plt.xlabel('Group', size=18)
        plt.ylabel(request['perf_ind'], size=18)

        plt.show()

        # fig = ax.get_figure()
        # fig.savefig("{}/{}.png".format(path, file_name))
        # plt.clf()

    def output_performance_file(self, request):
        performance_df = pd.DataFrame(
            columns=[
                'factor', 'strategy', 'window', 'method', 'group',
                'position', 'CAGR[%]', 'MDD[%]', 'MAR'
            ]
        )

        response = requests.get("http://{}/task/get_task_combi".format(self._api_server_IP), params=request)
        combination = json.loads(response.text)['result']
        
        for combi in combination:
            equity_df, _ = self._read_file(combi)
            ind_list, _ = self._compute_performance_ind(equity_df)

            performance_df = performance_df.append({
                'factor': self._general.factor_to_string(combi[0]),
                'strategy': combi[1],
                'window': combi[2],
                'method': combi[3],
                'group': combi[4],
                'position': combi[5],
                'CAGR[%]': ind_list[0][1],
                'MDD[%]': ind_list[0][2],
                'MAR': ind_list[0][3],
            }, ignore_index=True)
        
        print(performance_df)
        path = self._cfg.get_value('path', 'path_to_performance_indicator')
        performance_df.to_csv(path+'performance_indicator.csv')

    def query_performance_file(self):
        path = self._cfg.get_value('path', 'path_to_performance_indicator')
        performance_df = pd.read_csv(path+'performance_indicator.csv').drop('Unnamed: 0', axis=1)
        return performance_df

    def _read_file(self, param):
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
        return equity_df, performance_df

    def _read_request_files(self, request):
        equity_df = pd.DataFrame()

        response = requests.get("http://{}/task/get_task_combi".format(self._api_server_IP), params=request)
        combination = json.loads(response.text)['result']

        # 讀檔並串接 equity
        for param in combination:
            temp_equity_df, performance_df = self._read_file(param)

            if equity_df.empty:
                equity_df = temp_equity_df
            else:
                equity_df = equity_df.join(temp_equity_df)

        return equity_df, performance_df

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
        