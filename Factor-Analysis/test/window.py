import pandas as pd
import numpy as np
import datetime
import requests
import json
from package.backtest_handler import BacktestHandler


class Window:

    def __init__(self, window_config, t2_period, cal, fac):
        self.window_config = window_config
        self._t2_period = t2_period
        self._cal = cal
        self._fac = fac
        self._n_season = window_config['n_season']

        self._group_ticker = []
        self._start_equity = 0

        self._play_t1(t2_period[0])
        self._play_t2()
    
    # T1: 選股
    def _play_t1(self, date):
        if self.window_config['if_first'] == True:
            date = self._cal.get_trade_date(date, -2, 's')
        else:
            date = self._cal.get_trade_date(date, -1, 's')

        factor_df_dict = {}
        # 抓雙因子的資料
        for factor in self.window_config['factor_list']:
            factor_all_date_df = self._fac.factor_df_dict[factor]
            factor_df = factor_all_date_df.loc[date].to_frame()
            # 如果要多看前幾季的因子
            if self._n_season > 0:
                for i in range(self._n_season):
                    date = self._cal.get_trade_date(date, 1, 's')
                    temp_factor_df = factor_all_date_df.loc[date]
                    factor_df = factor_df.join(temp_factor_df)
                # 將這幾季的因子取平均
                factor_df['mean'] = factor_df.mean(axis=1)
                factor_df = factor_df['mean']
            factor_df_dict[factor] = factor_df

        if len(self.window_config['factor_list']) == 1:
            # 將因子的資料排序
            factor = self.window_config['factor_list'][0]
            group_list = self._fac.rank_factor(factor_df_dict[factor], factor)
            the_group_df = group_list[self.window_config['group'] - 1]
        
        elif len(self.window_config['factor_list']) == 2:
            first_factor = self.window_config['factor_list'][0]
            second_factor = self.window_config['factor_list'][1]

            # 先以第一個因子排序
            group_list = self._fac.rank_factor(factor_df_dict[first_factor], first_factor)
            # 選某一群標的
            the_group_ticker_list = group_list[self.window_config['group'] - 1]['ticker'].tolist()
            # 抓出這群所有標的 第二個因子的資料
            second_fac_group_df = factor_df_dict[second_factor].loc[the_group_ticker_list]
            # 用第二個因子資料再排名一次這群標的
            the_group_df = self._fac.rank_factor(second_fac_group_df, second_factor)[0]
        
        self._group_ticker = the_group_df['ticker'].tolist()

    # T2: 買進T1選的股 回測 記錄績效
    def _play_t2(self):
        # 交由 BacktestHandler 來抓股價 分配權重 回測
        backtest_handler = BacktestHandler(
            self.window_config,
            self._t2_period, self._group_ticker,
            self._cal
        )
        # # 回傳績效
        # backtest_result_dict = backtest_handler.backtest_result_dict
        # # 抓初始權重
        # self._start_equity = backtest_handler.weight
        
        # # 計算績效
        # self._compute_window_performance(backtest_result_dict)
        # # 更新投組目前的現金
        # self.window_config['cash'] = self.window_config['equity_df'].iloc[-1]['portfolio_equity']

        # if self.window_config['if_first'] == True:
        #     self.window_config['if_first'] = False

        backtest_result = backtest_handler.backtest_result
        self._start_equity = backtest_handler.start_equity
        self._compute_bbands_performance(backtest_result)
        self.window_config['cash'] = self.window_config['equity_df'].iloc[-1]['portfolio_equity']

        if self.window_config['if_first'] == True:
            self.window_config['if_first'] = False

    def _compute_window_performance(self, backtest_result_dict):
        # 第一個窗格時 需要先建好df格式給後面接上
        if self.window_config['if_first'] == True:
            performance_df = pd.DataFrame(
                columns=['ticker', 'start', 'end', 'start_equity', 'final_equity', 'return']
            )
            equity_df = pd.DataFrame(columns=['date', 'portfolio_equity'])
        else:
            # 後面的窗格直接讀即可
            performance_df = self.window_config['performance_df']
            equity_df = self.window_config['equity_df']
        
        equity_list = []
        count = 0
        for ticker, value in backtest_result_dict.items():
            # 第一次為空的DF 直接賦值
            if self.window_config['heatmap'].empty:
                self.window_config['heatmap'] = value['heatmap']
            else:
                # 後面不斷的疊圖
                self.window_config['heatmap'] = self.window_config['heatmap'].add(value['heatmap'], fill_value=0)

            performance_df = performance_df.append([{
                'ticker': ticker,
                'start': self._t2_period[0], 'end': self._t2_period[1],
                'start_equity': self._start_equity, 'final_equity': value['Equity Final [$]'],
                'return': value['Return [%]'],
            }], ignore_index=True)

            # 有資料的就把資料填上
            if not value['_equity_curve'].empty:
                df = value['_equity_curve']['Equity']
                # 要把第一&最後一筆刪掉因為抓股價時有多抓
                df = df.drop(df.index[[0, -1]])
                equity_list.append(df)
            else:
                # 計算回測失敗標的的數量
                count = count + 1

        self.window_config['performance_df'] = performance_df
        
        if count != self.window_config['position']:
            # 將投組內的每個標的的每日權益合併 變成整個投組的每日權益變化
            portfolio_equity_df = pd.concat(equity_list, axis=1)
            portfolio_equity_df.index.name = 'date'
            portfolio_equity_df['portfolio_equity'] = portfolio_equity_df.iloc[:, :].sum(axis=1)
            # 回測失敗的標的 都用初始資產當作權益變化
            portfolio_equity_df['portfolio_equity'] = portfolio_equity_df['portfolio_equity'].apply(
                lambda x: x+(count*self._start_equity)
            )
            equity_record = portfolio_equity_df[['portfolio_equity']].reset_index().to_dict('records')
        # 如果同一個窗格抓到的所有標的都失敗
        else:
            # 填上窗格第一天與最後一天 投組資產=初始資產*部位數量
            portfolio_equity = self._start_equity * self.window_config['position']
            equity_record = [
                {
                    'date': datetime.datetime.strptime(self._t2_period[0], '%Y-%m-%d'), 
                    'portfolio_equity': portfolio_equity,
                },
                {
                    'date': datetime.datetime.strptime(self._t2_period[1], '%Y-%m-%d'),
                    'portfolio_equity': portfolio_equity,
                },
            ]
        equity_df = equity_df.append(equity_record, ignore_index=True)
        self.window_config['equity_df'] = equity_df

    def _compute_bbands_performance(self, backtest_result):
        performance_df = self.window_config['performance_df']
        equity_df = self.window_config['equity_df']
        portfolio_equity_df = pd.DataFrame()

        for i, order in enumerate(backtest_result):
            flow_equity = pd.DataFrame()
            pre_end = ""

            for detail in order:
                temp_equity_df = detail['equity_df']

                if detail == order[0]:
                    flow_equity = temp_equity_df
                else:
                    if pre_end == detail['start']:
                        temp_equity_df = temp_equity_df.drop(temp_equity_df.index[0])
                    flow_equity = flow_equity.append(temp_equity_df)
                pre_end = detail['end']

                del detail['equity_df']
                performance_df = performance_df.append(detail, ignore_index=True)
                # print(temp_equity_df)
            
            flow_equity.columns = [i]
            
            if order == backtest_result[0]:
                portfolio_equity_df = flow_equity
            else:
                portfolio_equity_df = pd.concat([portfolio_equity_df, flow_equity], axis=1)

        portfolio_equity_df = portfolio_equity_df.fillna(method='ffill')
        portfolio_equity_df['portfolio_equity'] = portfolio_equity_df.iloc[:, :].sum(axis=1)
        equity_record = portfolio_equity_df[['portfolio_equity']].reset_index().to_dict('records')
        equity_df = equity_df.append(equity_record, ignore_index=True)

        self.window_config['performance_df'] = performance_df
        self.window_config['equity_df'] = equity_df
        # print(performance_df)
        # print(equity_df)
