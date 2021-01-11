import talib
import requests
import json

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

from modules.factor import Factor


server_ip = "http://140.115.87.197:8090/"

class BuyAndHold(Strategy):

    def set_param(self, factor, ticker, cal):
        self.factor = factor
        self.ticker = ticker
        self.cal = cal


    def init(self):
        super().init()
        self.buy_date_list = []
        self.sell_date_list = []

        self.start_date = self.data.index[0].strftime('%Y-%m-%d')
        self.end_date = self.data.index[-1].strftime('%Y-%m-%d')
        report_date_list = self.cal.get_report_date_list(self.start_date, self.end_date)

        flag = 0
        for date in report_date_list:
            if date.split("-")[1] == "03":
                how = 1
            else:
                how = 0
            fac_date = self.cal.advance_date(date, how, 's')

            rank_list = Factor(self.factor, fac_date).rank_factor()
            tier_1_ticker_list = rank_list[0]['ticker'].tolist()

            if flag == 0 and self.ticker in tier_1_ticker_list:
                flag = 1
                self.buy_date_list.append(date)
            elif flag == 1 and self.ticker not in tier_1_ticker_list:
                flag = 2
                self.sell_date_list.append(date)
            elif flag == 2 and self.ticker in tier_1_ticker_list:
                flag = 1
                self.buy_date_list.append(date)


    def next(self):
        super().next()
        today = self.data.index[-1].strftime('%Y-%m-%d')
        if today in self.buy_date_list:
            self.buy()
        elif today in self.sell_date_list:
          for trade in self.trades:
            trade.close()
