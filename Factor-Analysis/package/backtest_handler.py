import pandas as pd
import numpy as np
import datetime
import requests
import json
import pathos
from multiprocessing import Pool
from backtesting import Backtest, Strategy
from utils.config import Config
from strategy.buy_and_hold import BuyAndHold
from strategy.bbands import BBands


class BacktestHandler:

    def __init__(self, window_config, t2_period, ticker_list, cal):
        self._window_config = window_config
        self._t2_period = t2_period
        self._ticker_list = ticker_list
        self._cal = cal

        self._cfg = Config()

        stk_price_dict = self._get_stk_price()
        self.weight_dict = self._set_weight()
        self.backtest_result_dict = self._do_backtesting(stk_price_dict)

    def _get_stk_price(self):
        api_server_IP = self._cfg.get_value('IP', 'api_server_IP')

        payloads = {
            'ticker_list': self._ticker_list,
            # 因為 backtesting 不能在第一天跟最後一天交易 所以必須往前後多加一天
            'start_date': self._cal.get_trade_date(self._t2_period[0], -2, 'd'),
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
        
    def _set_weight(self):
        # 平均分配資金
        weight_dict = {}
        weight = self._window_config['cash'] / len(self._ticker_list)

        for ticker in self._ticker_list:
            weight_dict[ticker] = weight
        return weight_dict

    def _do_backtesting(self, stk_price_dict):
        commission = float(self._cfg.get_value('parameter', 'commission'))
        min_ma = int(self._cfg.get_value('parameter', 'min_ma'))
        max_ma = int(self._cfg.get_value('parameter', 'max_ma'))
        ma_step = int(self._cfg.get_value('parameter', 'ma_step'))
        min_band_width = float(self._cfg.get_value('parameter', 'min_band_width'))
        max_band_width = float(self._cfg.get_value('parameter', 'max_band_width'))
        band_width_step = float(self._cfg.get_value('parameter', 'band_width_step'))

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
                        cash=int(self.weight_dict[ticker]),
                        commission=commission,
                        exclusive_orders=True,
                        trade_on_close=True # 可以在訊號觸發當天收盤價買
                    )
                    result = bt.run()
                elif self._window_config['strategy'] == 2:
                    bt = Backtest(
                        stk_price_dict[ticker],
                        BBands,
                        cash=int(self.weight_dict[ticker]),
                        commission=commission,
                        exclusive_orders=True
                    )
                    # result = bt.run()
                    result = bt.optimize(
                        ma_len=range(min_ma, max_ma, ma_step),
                        band_width=list(np.arange(min_band_width, max_band_width, band_width_step))
                    )
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
                    'Return [%]': 0,
                    '_equity_curve': pd.DataFrame(),
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
