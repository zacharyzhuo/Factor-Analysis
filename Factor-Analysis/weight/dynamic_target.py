import pandas as pd
import numpy as np


class DynamicTarget:

    def __init__(self, window_config, profit_table, trade_dict):
        self._window_config = window_config
        self._profit_table = profit_table
        self._trade_dict = trade_dict
        self._position = window_config['position']

    def get_weight(self, method):
        weight_table = self._profit_table.copy()
        weight_table.loc[:, :] = np.nan

        # 預先創好所有可能會有的金流 陣列位置代表金流編號
        cash_flow = [[] for _ in range(self._position)]
        # 編號佇列
        number_queue = [x for x in range(self._position)]
        # 避免重複標的
        ticker_list = []
        weight = 1 / self._position
        # 紀錄重新分配權重日子
        reallocate_date = []

        # 每一天每個標的檢查
        for date in self._profit_table.index:
            # 每天變化的標的
            daily_ticker = []
            if_reallocate = False

            # 如果目前有持有標的就要檢查當天是否會出場
            if len(ticker_list) != 0:
                # 必須要複製一份 避免執行迴圈與刪除元素衝突
                temp_ticker_list = ticker_list.copy()
                
                for ticker in temp_ticker_list:
                    end_date = self._trade_dict[ticker][0][1]
                    # 代表金流編號 以及 要放在 cash_flow 哪個位置
                    number = self._trade_dict[ticker][0][2]

                    if date == end_date:
                        ticker_list.remove(ticker)
                        # 還號碼牌
                        number_queue.append(number)
                        self._trade_dict[ticker].pop(0)
                        if_reallocate = True
                    else:
                        daily_ticker.append(ticker)
                    
                    weight_table.loc[date, ticker] = '-'

            for ticker in self._profit_table.columns:

                if len(self._trade_dict[ticker]) != 0:
                    start_date = self._trade_dict[ticker][0][0]
                    end_date = self._trade_dict[ticker][0][1]

                    # 投組還沒裝滿繼續找
                    if len(ticker_list) < self._position:
                        # 標的不重複 且 今天=進場時間 且 非最後一天
                        # 排除最後一天出場又找新標的的情況
                        if ticker not in ticker_list and \
                            date == start_date and \
                            date != self._profit_table.index[-1]:

                            ticker_list.append(ticker)
                            # 發號碼牌 從號碼牌佇列刪除
                            number = number_queue.pop(0)
                            # 持有標的當中 需紀錄它是在哪個金流號碼
                            self._trade_dict[ticker][0].append(number)
                            daily_ticker.append(ticker)
                            if_reallocate = True

                            # 每個金流第一筆皆為初始資金依照權重所分配
                            if len(cash_flow[number]) == 0:
                                weight_table.loc[date, ticker] = weight
                            # 中間換股過後初始權重為前一筆交易的最後賺賠
                            else:
                                weight_table.loc[date, ticker] = '-'
                            
                            cash_flow[number].append({
                                'ticker': ticker,
                                'start_date': start_date,
                                'end_date': end_date,
                            })
                    else:
                        break
                else:
                    continue

            # 隨時讓投組保持滿水位
            # 當尋找到新標的時 & 有部位出場時要重新分配
            if method == 1 and if_reallocate == True:
                if len(daily_ticker) != 0:
                    weight_list = [1/len(daily_ticker) for x in range(len(daily_ticker))]
                    weight_table.loc[date, daily_ticker] = weight_list
                    reallocate_date.append(date)

        return weight_table, cash_flow, reallocate_date
