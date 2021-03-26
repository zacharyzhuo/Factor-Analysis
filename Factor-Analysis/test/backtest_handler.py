import pandas as pd
import numpy as np
import datetime
import requests
import json
import pathos
from multiprocessing import Pool
from talib import BBANDS
from backtesting import Backtest, Strategy
from utils.config import Config
from strategy.buy_and_hold import BuyAndHold
from strategy.bbands import BBands
from utils.plot import Plot


class BacktestHandler:

    def __init__(self, window_config, t2_period, group_ticker, cal):
        self._window_config = window_config
        self._t2_period = t2_period
        self._group_ticker = group_ticker
        self._cal = cal

        self._cfg = Config()
        # 為了要多往前先把MA算出來所以需要多抓這些天數
        self._max_ma = int(self._cfg.get_value('parameter', 'max_ma'))
        self.start_equity = 0

        stk_price_dict = self._get_stk_price()
        # self.weight_dict = self._set_weight()
        # self.backtest_result_dict = self._run_backtest(stk_price_dict)

        order_list = self._preprocess_signal(stk_price_dict)
        self.backtest_result = self._run_bbands_backtest(stk_price_dict, order_list)

    def _get_stk_price(self):
        api_server_IP = self._cfg.get_value('IP', 'api_server_IP')

        payloads = {
            'ticker_list': self._ticker_list,
            # 因為 backtesting 不能在第一天跟最後一天交易 所以必須往前後多加一天
            # 為了要多往前先把MA算出來所以需要多抓這些天數
            'start_date': self._cal.get_trade_date(self._t2_period[0], (1+self._max_ma)*-1, 'd'),
            'end_date': self._cal.get_trade_date(self._t2_period[1], 1, 'd'),
        }
        response = requests.get("http://{}/stk/get_ticker_period_stk".format(api_server_IP), params=payloads)
        stk_price_dict = json.loads(response.text)['result']

        for ticker in self._ticker_list:
            stk_df = pd.DataFrame(stk_price_dict[ticker]).drop(['index', 'outstanding_share'], axis=1)
            stk_df['date'] = [datetime.datetime.strptime(elm, "%Y-%m-%d") for elm in stk_df['date']]
            stk_df.set_index("date", inplace=True)
            # 資料庫抓出來會按照字母排序
            stk_df.columns = ['Close', 'High', 'Low', 'Open', 'Volume']
            stk_df = stk_df.dropna()
            stk_price_dict[ticker] = stk_df
        return stk_price_dict
    
    def _preprocess_signal(self, stk_price_dict):
        df = pd.DataFrame()

        # 預處理該群所有標的的訊號
        for ticker, stk_df in stk_price_dict.items():
            try:
                # 用 ta-lib 算出布林通道
                up_band, mid, down_band = BBANDS(
                    stk_df['Close'], timeperiod=50,
                    nbdevup=1.5, nbdevdn=1.5,
                    matype=0
                )
                # 抓出買賣訊號 都沒有:0 買:1 賣:2
                buy_signal = (stk_df['Close'] > up_band).replace(True, 1)
                sell_signal = (stk_df['Close'] < down_band).replace(True, 2)
                signal = buy_signal + sell_signal
                stk_df[ticker] = signal.astype('int')

                # 因為前面有往前多抓幾天為了算出均線 現在把多的日子刪掉
                strat_date = datetime.datetime.strptime(self._t2_period[0], "%Y-%m-%d")
                end_date = datetime.datetime.strptime(self._t2_period[1], "%Y-%m-%d")
                stk_df = stk_df[[ticker]][strat_date: end_date]

                if df.empty:
                    df = stk_df
                else:
                    df = df.join(stk_df)
            except Exception as e:
                print("[Error]: <{}> {}".format(ticker, e))
                # 把全部缺值或有錯的標的都刪掉
                self._ticker_list.remove(ticker)
                continue
        # 依照因子排列順序排列
        df = df[self._ticker_list]

        pick_dict = {}
        pick_list = []
        # 預先宣告與最大持有股數的編號 一樣的編號代表需要放一起回測
        number_queue = [x for x in range(self._window_config['position'])]

        # 抓出將要進行買賣的標的與時間區段
        for date, row in df.iterrows():
            # 同一天
            # 如果目前已經有觸發買進訊號的標的在 pick_list 優先檢查是否觸發出場訊號
            if len(pick_list) != 0:
                pick_row = row.loc[pick_list]
                for i in range(len(pick_row)):
                    if pick_row[i] == 2:
                        # 出發賣出訊號後 把end_date改為當天 並從 pick_list 移除
                        pick_dict[pick_row.index[i]]['end_date'] = date.strftime('%Y-%m-%d')
                        pick_list.remove(pick_row.index[i])
                        # 出場的編號 擺在編號佇列最後面 先進先出
                        number_queue.append(pick_dict[pick_row.index[i]]['number'])
            
            for j in range(len(row)):
                # 如果 pick_list 未到達持有部位上限 持續尋找觸發訊號的標的
                if len(pick_list) < self._window_config['position']:
                    # 找不重複且已經觸發買進訊號的標的
                    if row.index[j] not in pick_list and row[j] == 1:
                        pick_list.append(row.index[j])
                        pick_dict[row.index[j]] = {
                            # 優先用編號佇列最前面的編號
                            'number': number_queue.pop(0),
                            'start_date': date.strftime('%Y-%m-%d'),
                            'end_date': self._t2_period[1],
                        }
                # 找到滿就不繼續找
                else:
                    break
        # 把編號一樣的排在一起
        print(pick_dict)
        order = {}

        for ticker, value in pick_dict.items():
            if value['number'] in order:
                order[value['number']].append({
                    'ticker': ticker,
                    'start_date': value['start_date'],
                    'end_date': value['end_date'],
                })

            else:
                order[value['number']] = [{
                    'ticker': ticker,
                    'start_date': value['start_date'],
                    'end_date': value['end_date'],
                }]
        return list(order.values())

    def _run_backtest(self, stk_price_dict):
        min_ma = int(self._cfg.get_value('parameter', 'min_ma'))
        ma_step = int(self._cfg.get_value('parameter', 'ma_step'))
        min_band_width = float(self._cfg.get_value('parameter', 'min_band_width'))
        max_band_width = float(self._cfg.get_value('parameter', 'max_band_width'))
        band_width_step = float(self._cfg.get_value('parameter', 'band_width_step'))
        commission = float(self._cfg.get_value('parameter', 'commission'))
        weight = int(self._window_config['cash'] / self._window_config['position'])

        backtest_result_dict = {}

        # 使用 inner function 特別獨立出需要多核運算的部分
        def multiprocessing_job(ticker):
            try:
                if self._window_config['strategy'] == 0 or self._window_config['strategy'] == 1:
                    # 傳入窗格開始與結束時間 即買點與賣點
                    BuyAndHold.set_param(BuyAndHold, [self._t2_period[0]],  [self._t2_period[1]])
                    bt = Backtest(
                        stk_price_dict[ticker],
                        BuyAndHold,
                        cash=weight,
                        commission=commission,
                        exclusive_orders=True,
                        trade_on_close=True # 可以在訊號觸發當天收盤價買
                    )
                    result = bt.run()
                elif self._window_config['strategy'] == 2:
                    bt = Backtest(
                        stk_price_dict[ticker],
                        BBands,
                        cash=weight,
                        commission=commission,
                        exclusive_orders=True
                    )
                    result, heatmap = bt.optimize(
                        ma_len=range(min_ma, self._max_ma, ma_step),
                        band_width=[round(x, 1) for x in np.arange(
                            min_band_width, max_band_width+0.1, band_width_step
                        )],
                        maximize='Equity Final [$]',
                        return_heatmap=True,
                    )
                    hm = heatmap.groupby(['ma_len', 'band_width']).mean().unstack()
                    result['heatmap'] = hm
                    print(result._strategy)
                # print(result)
                # bt.plot()
                return {ticker: result}
            except Exception as e:
                print("[ticker {}]: <{} to {}> {}".format(
                    ticker, self._t2_period[0], self._t2_period[1], e)
                )
                return {ticker: {
                    'Equity Final [$]': self.weight_dict[ticker],
                    'Return [%]': np.nan,
                    '_equity_curve': pd.DataFrame(),
                    'heatmap': pd.DataFrame(),
                }}
        
        # 因為有使用 inner function 所以要使用 pathos 的 multiprocessing 而非 python 原生的
        # Pool() 不放參數則默認使用電腦核的數量
        pool = pathos.multiprocessing.Pool()
        results = pool.map(multiprocessing_job, self._ticker_list) 
        pool.close()
        pool.join()

        for result in results:
            if result:
                backtest_result_dict[list(result.keys())[0]] = list(result.values())[0]
        return backtest_result_dict

    def _run_bbands_backtest(self, stk_price_dict, order_list):
        commission = float(self._cfg.get_value('parameter', 'commission'))
        self.start_equity = int(self._window_config['cash'] / self._window_config['position'])

        # 使用 inner function 特別獨立出需要多核運算的部分
        def multiprocessing_job(order):
            weight = self.start_equity
            result_list = []

            for detail in order:
                try:
                    BuyAndHold.set_param(BuyAndHold, [detail['start_date']],  [detail['end_date']])
                    bt = Backtest(
                        stk_price_dict[detail['ticker']],
                        BuyAndHold,
                        cash=weight,
                        commission=commission,
                        exclusive_orders=True,
                        trade_on_close=True # 可以在訊號觸發當天收盤價買
                    )
                    result = bt.run()

                    strat_date = datetime.datetime.strptime(detail['start_date'], "%Y-%m-%d")
                    end_date = datetime.datetime.strptime(detail['end_date'], "%Y-%m-%d")
                    equity_df = result['_equity_curve'][['Equity']][strat_date: end_date]
                    result_list.append({
                        'ticker': detail['ticker'],
                        'start': detail['start_date'],
                        'end': detail['end_date'],
                        'start_equity': weight,
                        'final_equity': result['Equity Final [$]'],
                        'return': result['Return [%]'],
                        'equity_df': equity_df,
                    })
                    weight = result['Equity Final [$]']

                except Exception as e:
                    print("[ticker {}]: <{} to {}> {}".format(
                        detail['ticker'], detail['start_date'], detail['end_date'], e)
                    )
                    pass
            return result_list
        
        # 因為有使用 inner function 所以要使用 pathos 的 multiprocessing 而非 python 原生的
        # Pool() 不放參數則默認使用電腦核的數量
        pool = pathos.multiprocessing.Pool()
        results = pool.map(multiprocessing_job, order_list) 
        pool.close()
        pool.join()

        return results
