import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime
from itertools import product
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from utils.config import Config
from utils.general import General
from service.calendar import Calendar


COLOR = [
    'red', 'darkorange', 'gold', 'green',
    'skyblue', 'blue', 'purple', 'black',
    'grey', 'pink', 'lime',  'brown',
]

# COLOR = [
#     'red', 'darkorange', 'green'
# ]


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
        # ax = equity_df.plot.line(figsize=(12, 8), color=COLOR[0])
        ax.set_xlabel('Date')
        ax.set_ylabel('Equity')

        # 加上千位數逗點
        ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda x, p: format(int(x), ','))
        )

        # 強調Y軸上某一個點
        ax.axhline(10000000, color='black', linestyle='--')

        # 顯示文字註解
        plt.text(
            # equity_df.index[200], equity_max/10*9,
            equity_df.index[500], 8000000,
            perf_ind_inf_str,
            size=14, ha='left', va='top',
            bbox=dict(
                facecolor='gray', alpha=1.5, edgecolor='gray'
            )
        )

        plt.show()

    def plot_equity_curve_and_cap_util_rate(self, request):
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
                perf_ind_inf_str = perf_ind_inf_str + "[{}] CAGR: {}%, MDD: {}%\n".format(
                    elm[0], elm[1], elm[2]
                )
            else:
                perf_ind_inf_str = perf_ind_inf_str + "[{}] CAGR: {}%, MDD: {}%".format(
                    elm[0], elm[1], elm[2]
                )

        perf_ind_inf_str = perf_ind_inf_str + "\nFull Use of Equity Rate: {}%".format(
            100 - round(df.loc[df['cap_util'] != position].shape[0] / df.shape[0] * 100, 2)
        )

        # ax = equity_df.iloc[:, :-1].plot.line(figsize=(12, 8))
        ax = equity_df.iloc[:, :-1].plot.line(figsize=(12, 8), color=[COLOR[1], COLOR[2]])

        # 顯示文字註解
        plt.text(
            # equity_df.index[1], equity_df[equity_df.columns[0]].min(),
            equity_df.index[0], 3580000,
            perf_ind_inf_str,
            size=13, ha='left', va='top',
            bbox=dict(
                facecolor='gray', alpha=1.5, edgecolor='gray'
            )
        )

        ax2 = equity_df['cap_util_rate'].plot.line(color='grey', secondary_y=True)
        
        # 強調Y軸上某一個點
        ax.axhline(10000000, color='black', linestyle='--')
        
        # 加上千位數逗點
        ax.get_yaxis().set_major_formatter(
            FuncFormatter(lambda x, p: format(int(x), ','))
        )
        
        ax.set_xlabel("Date")
        ax.set_ylabel("Equity")
        ax2.set_ylabel("Capital Utilization Rate[%]")

        plt.ylim(-10, 110)

        plt.show()

    def plot_performance_heatmap(self, request):
        heatmap_df = pd.DataFrame(columns=[6, 15, 60, 150, 300])

        df = self.read_performance_file()
        df = df.loc[
            (df['factor'] == request['factor']) &
            (df['strategy'] == request['strategy']) &
            (df['window'] == request['window']) &
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

        # ax.set_title("[{}] {}_{}_{}".format(
        #     request['perf_ind'], request['factor'],
        #     request['window'], request['method'])
        # )
        print("[{}] {}_{}_{}_{}".format(
                request['perf_ind'], request['factor'],
                request['strategy'], request['window'],
                request['method']
            )
        )

        plt.show()

    def plot_profit_bar_chart(self, request):
        equity_df, trade_df = self._read_request_files(request)
        file_name = equity_df.columns[0]

        trade_df['win'] = trade_df['return'].apply(lambda x: 1 if x > 0 else 0)
        win_rate = round(trade_df['win'].sum() / trade_df.shape[0] * 100, 2)
        lose_rate = round(100 - win_rate, 2)

        trade_df['+0-20'] = trade_df['return'].apply(lambda x: 1 if x > 0 and x <= 20 else 0)
        trade_df['+20-100'] = trade_df['return'].apply(lambda x: 1 if x > 20 and x <= 100 else 0)
        trade_df['+100<'] = trade_df['return'].apply(lambda x: 1 if x > 100 else 0)

        trade_df['-0-20'] = trade_df['return'].apply(lambda x: 1 if x <= 0 and x >= -20 else 0)
        trade_df['-20>'] = trade_df['return'].apply(lambda x: 1 if x < -20 else 0)

        positive_df = trade_df.copy()
        positive_df['return'] = positive_df['return'].apply(lambda x: 0 if x < 0 else x)
        negative_df = trade_df.copy()
        negative_df['return'] = negative_df['return'].apply(lambda x: 0 if x >= 0 else x)

        text_str = "{}\n--------------------------------\n100 <:  {}\n20 ~ 100: {}\n0 ~ 20: {}\n--------------------------------\n0 ~ -20: {}\n-20 >: {}\n--------------------------------\nTotal Trades Number: {}\nWin Rate: {}\nLose Rate: {}".format(
            file_name,
            trade_df['+100<'].sum(), trade_df['+20-100'].sum(), trade_df['+0-20'].sum(), 
            trade_df['-0-20'].sum(), trade_df['-20>'].sum(), 
            len(trade_df.index), win_rate, lose_rate
        )

        fig = plt.figure(figsize=(80, 8))
        sns.set_theme(style="whitegrid")

        ax = sns.barplot(x="index", y="return", data=positive_df.reset_index(), color="navy")
        ax = sns.barplot(x="index", y="return", data=negative_df.reset_index(), color="gray")
        plt.legend()

        plt.xlabel("Trade Series Number")
        plt.ylabel("Return[%]")

        plt.xticks(fontsize=2, rotation=90)
        plt.yticks(fontsize=12)

        # 顯示文字註解
        plt.text(
            trade_df.index[200], trade_df['return'].max(),
            # trade_df.index[180], 90,
            text_str,
            size=14, ha='left', va='top',
            bbox=dict(
                facecolor='gray', alpha=1.5, edgecolor='gray'
            )
        )

        plt.show()
    
    def plot_window_profit_bar_chart(self, request):
        equity_df, _ = self._read_request_files(request)
        file_name = equity_df.columns[0]
        report_date_list = self._cal.get_report_date_list(self._start_date, self._end_date)

        window_return = []
        peroid_list = []

        # 窗格數量會比期間內財報公布日數量多一個
        for i in range(len(report_date_list)+1):

            # 第一個窗格T2: 回測期間第一個交易日~第一個財報公布日
            if i == 0:
                date = self._cal.get_trade_date(self._start_date, 0, 'd')
                peroid_list.append(date)
                strat_equity = equity_df.loc[date, file_name]
                final_equity = equity_df.loc[report_date_list[i], file_name]
                final_equity = final_equity.iloc[0]

            # 最後一個窗格T2: 最後一個財報公布日~回測期間最後一個交易日
            elif i == len(report_date_list):
                date = self._cal.get_trade_date(self._end_date, -1, 'd')
                peroid_list.append(report_date_list[i-1])
                strat_equity = equity_df.loc[report_date_list[i-1], file_name]
                final_equity = equity_df.loc[date, file_name]
                strat_equity = strat_equity.iloc[0]

            # 其他窗格T2: 兩公布日之間 
            else:
                peroid_list.append(report_date_list[i-1])
                strat_equity = equity_df.loc[report_date_list[i-1], file_name]
                final_equity = equity_df.loc[report_date_list[i], file_name]
                strat_equity = strat_equity.iloc[0]
                final_equity = final_equity.iloc[0]

            window_return.append(round((final_equity-strat_equity)/strat_equity*100, 2))

        window_return_df = pd.DataFrame(window_return, columns=['return'])
        window_return_df['window_peroid'] = peroid_list
        total_return = (equity_df.iloc[-1, 0]-10000000) / 10000000 * 100

        positive_df = window_return_df.copy()
        positive_df['return'] = positive_df['return'].apply(lambda x: 0 if x < 0 else x)
        negative_df = window_return_df.copy()
        negative_df['return'] = negative_df['return'].apply(lambda x: 0 if x >= 0 else x)

        result, _ = self._compute_performance_ind(equity_df)

        text_str = "{}\nCAGR: {}%, MDD: {}%".format(
            file_name, result[0][1], result[0][2]
        )

        fig = plt.figure(figsize=(12, 7))
        sns.set_theme(style="whitegrid")

        ax = sns.barplot(x="window_peroid", y="return", data=positive_df, color="cornflowerblue")
        ax = sns.barplot(x="window_peroid", y="return", data=negative_df, color="gray")
        plt.legend()

        plt.xlabel("Start Date of Window", fontsize=8)
        plt.ylabel("Return[%]")

        plt.xticks(fontsize=8, rotation=35)
        plt.yticks(fontsize=12)
        # 顯示文字註解
        plt.text(
            17, window_return_df['return'].max()-2,
            text_str,
            size=13, ha='left', va='top',
            bbox=dict(
                facecolor='gray', alpha=1.5, edgecolor='gray'
            )
        )

        plt.show()
    
    def plot_linear_regression(self, request):
        p_df = self.read_performance_file()
        lr_df = self.read_regression_file()
        factor_str_list = []
        query_index = "{}_{}_{}_{}".format(
            request['strategy'], request['window'],
            request['method'], request['position'],
        )
        print(lr_df.loc[
            (lr_df['perf_ind'] == request['perf_ind']) &
            (lr_df['index'] == query_index)
        ])
        
        lr_df = lr_df.loc[
            (lr_df['perf_ind'] == request['perf_ind']) &
            (lr_df['index'] == query_index)
        ].set_index('index').T.drop('perf_ind')
        print(lr_df.sort_values(by=[query_index]))

        path = self._cfg.get_value('path', 'path_to_performance_analysis')
        lr_df.sort_values(by=[query_index]).to_csv(path+'lr_df.csv')

        fig = plt.figure(figsize=(8, 7))

        for i, factor in enumerate(request['factor_list']):
            factor_str = self._general.factor_to_string(factor)
            factor_str_list.append(factor_str)

            temp_df = p_df.loc[
                (p_df['factor'] == factor_str) &
                (p_df['strategy'] == request['strategy']) &
                (p_df['window'] == request['window']) &
                (p_df['method'] == request['method']) &
                (p_df['position'] == request['position'])
            ]

            ax = sns.regplot(x=temp_df['group'], y=temp_df[request['perf_ind']], color=COLOR[i])
            ax.set(xticks=range(1, len(temp_df['group'])+1, 1))

        plt.legend(labels=factor_str_list)

        plt.xlabel('Group', fontsize=12)
        plt.ylabel(request['perf_ind'], fontsize=12)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)

        plt.show()

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
        path = self._cfg.get_value('path', 'path_to_performance_analysis')
        performance_df.to_csv(path+'performance_indicator.csv')
        # performance_df.to_csv(path+'performance_indicator_a&na.csv')

    def output_linear_regression_file(self, request):
        df = self.read_performance_file()
        combination = []
        lr_df = pd.DataFrame()
        column_order = ['index', 'perf_ind']

        data = (
            request['strategy_list'], request['window_list'], 
            request['method_list'], request['position_list']
        )

        for combi in product(*data):
            # strategy: B&H
            if combi[0] == 0:
                # B&H 排除0之外的窗格 排除等權重之外的方法
                if combi[1] != 0 or combi[2] != 0: 
                    continue
            
            combination.append(combi)
        
        for perf_ind in request['perf_ind_list']:
            for c in combination:
                factor_b1_val_dict = {}
                factor_b1_val_dict["index"] = "{}_{}_{}_{}".format(
                    c[0], c[1], c[2], c[3]
                )

                for i, factor in enumerate(request['factor_list']):
                    factor_str = self._general.factor_to_string(factor)
                    
                    # if len(column_order) != 14:
                    if len(column_order) != 3:
                        column_order.append(factor_str)

                    temp_df = df.loc[
                        (df['factor'] == factor_str) &
                        (df['strategy'] == c[0]) &
                        (df['window'] == c[1]) &
                        (df['method'] == c[2]) &
                        (df['position'] == c[3])
                    ]

                    x = self._compute_simple_linear_regression(temp_df['group'], temp_df[perf_ind])
                    factor_b1_val_dict[factor_str] = round(x[1], 3)

                factor_b1_val_dict['perf_ind'] = perf_ind
                lr_df = lr_df.append(factor_b1_val_dict, ignore_index=True)
        
        lr_df = lr_df[column_order]
        print(lr_df)
        path = self._cfg.get_value('path', 'path_to_performance_analysis')
        lr_df.to_csv(path+'regression_b1.csv')  
        # lr_df.to_csv(path+'regression_b1_a&na.csv')  

    def read_performance_file(self):
        path = self._cfg.get_value('path', 'path_to_performance_analysis')
        df = pd.read_csv(path+'performance_indicator.csv').drop('Unnamed: 0', axis=1)
        # df = pd.read_csv(path+'performance_indicator_a&na.csv').drop('Unnamed: 0', axis=1)
        return df
    
    def read_regression_file(self):
        path = self._cfg.get_value('path', 'path_to_performance_analysis')
        df = pd.read_csv(path+'regression_b1.csv').drop('Unnamed: 0', axis=1)
        # df = pd.read_csv(path+'regression_b1_a&na.csv').drop('Unnamed: 0', axis=1)
        return df

    def _compute_simple_linear_regression(self, raw_x, raw_y):
        n = np.size(raw_x)
        x = np.array(raw_x)
        y = np.array(raw_y)
        x_mean = np.mean(x)
        y_mean = np.mean(y)

        num1 = np.sum(y*x) - n*y_mean*x_mean
        num2 = np.sum(x*x) - n*x_mean*x_mean
        
        b_1 = num1 / num2
        b_0 = y_mean - b_1 * x_mean
        
        return (b_0, b_1)

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

            result.append([col, round(cagr, 2), round(MDD, 2), round(MAR, 3)])

            if equity_df.max() > equity_max:
                equity_max = equity_df.max()
        
        return result, equity_max

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

        # combination = [
        #     [['EV_EBITDA'], 0, 0, 0, 1, 6],
        #     [['EV_EBITDA'], 1, 0, 0, 1, 6],
        #     [['EV_EBITDA'], 1, 1, 0, 1, 6],
        #     [['EV_EBITDA'], 1, 2, 0, 1, 6],
        # ]

        # 讀檔並串接 equity
        for param in combination:
            temp_equity_df, performance_df = self._read_file(param)

            if equity_df.empty:
                equity_df = temp_equity_df
            else:
                equity_df = equity_df.join(temp_equity_df)

        return equity_df, performance_df
  