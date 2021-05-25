# from sklearn import preprocessing
import pandas as pd
import numpy as np
from utils.config import Config


class FixedTarget:

    def __init__(self, window_config, profit_table, trade_dict):
        self._window_config = window_config
        self._profit_table = profit_table
        self._trade_dict = trade_dict
        self._position = window_config['position']

        self._cfg = Config()
        self._special_factor_list = self._cfg.get_value('factor', 'special_factor_list').split(",")

    def get_weight(self, method):
        # 複製 eauity table 並將內容清空
        weight_table = self._profit_table.copy()
        weight_table.loc[:, :] = np.nan

        # 當回測失敗標的過多 有可能選不滿
        position = min(self._position, len(self._profit_table.columns))
        # 預先創好所有可能會有的金流 陣列位置代表金流編號
        cash_flow = [[] for _ in range(position)]
        ticker_list = list(self._profit_table.columns[:position])

        # 等權重配置法
        if method == 0:
            weight = {}
            for ticker in ticker_list:
                weight[ticker] = 1 / position
        
        # # 基本面加權法
        # elif method == 1:
        #     factor_data = self._window_config['factor_data']

        #     # 單因子
        #     if len(self._window_config['factor']) == 1:
        #         factor = self._window_config['factor'][0]
        #         fac_df = factor_data[factor]
                
        #         if factor in self._special_factor_list:
        #             # 取倒數
        #             fac_df[factor] = fac_df[factor].apply(lambda x: np.nan if x == None else 1/float(x))

        #         # 正規化
        #         minmax = preprocessing.MinMaxScaler()
        #         data_minmax = minmax.fit_transform(fac_df)
        #         fac_df.loc[:, factor] = data_minmax
            
        #     # 雙因子
        #     elif len(self._window_config['factor']) == 2:
        #         first_factor = self._window_config['factor'][0]
        #         second_factor = self._window_config['factor'][1]

        #         for factor in self._window_config['factor']:
        #             if factor in self._special_factor_list:
        #                 # 取倒數
        #                 factor_data[factor][factor] = factor_data[factor][factor].apply(
        #                     lambda x: np.nan if x == None else 1/float(x)
        #                 )

        #         fac_df = factor_data[first_factor]
        #         data_minmax = preprocessing.MinMaxScaler().fit_transform(fac_df)
        #         fac_df.loc[:, first_factor] = data_minmax
        #         data_minmax = preprocessing.MinMaxScaler().fit_transform(factor_data[second_factor])
        #         fac_df.loc[:, second_factor] = data_minmax

        #     # 計算權重
        #     fac_df = fac_df.loc[ticker_list]
        #     # 雙因子需要將兩因子分數加總
        #     fac_df['score'] = fac_df.iloc[:, :].sum(axis=1)
        #     total = fac_df['score'].sum()
        #     fac_df['weight'] = fac_df['score'].apply(lambda x: x/total)
        #     weight = fac_df['weight'].to_dict()

        # 每天檢查
        for date in self._profit_table.index:
            # 因為只固定選前幾個標的 所以每天檢查這些就好
            for i, ticker in enumerate(ticker_list):
                if len(self._trade_dict[ticker]) != 0:
                    start_date = self._trade_dict[ticker][0][0]
                    end_date = self._trade_dict[ticker][0][1]

                    if date == start_date:
                        # 每個金流第一次買進標的才填入權重 
                        # 因為進出過後的錢已經不等於當初分配的錢
                        if len(cash_flow[i]) == 0:
                            weight_table.loc[date, ticker] = weight[ticker]
                        else:
                            weight_table.loc[date, ticker] = '-'
                        
                        # 布林通道在一個金流底下可能會進出多次
                        cash_flow[i].append({
                            'ticker': ticker,
                            'start_date': start_date,
                            'end_date': end_date,
                        })
                    
                    # 持有的時間填上 -
                    elif date > start_date and date <= end_date:
                        weight_table.loc[date, ticker] = '-'

                        # 出場後把這筆交易刪掉
                        if date == end_date:
                            self._trade_dict[ticker].pop(0)
        
        return weight_table, cash_flow, []
