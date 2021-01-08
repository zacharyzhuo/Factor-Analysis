import talib
import requests
import json

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

from modules.factor import Factor


server_ip = "http://140.115.87.197:8090/"
report_date = ['05-15', '08-14', '11-14', '03-31']

class BuyAndHold(Strategy):
    factor = ""
    ticker = ""
    start_date = ""
    end_date = ""
    buy_date_list = []
    sell_date_list = []

    def set_param(self, factor, ticker, cal):
        self.factor = factor
        self.ticker = ticker
        self.cal = cal

    def init(self):
        super().init()
        self.start_date = self.data.index[0].strftime('%Y-%m-%d')
        self.end_date = self.data.index[-1].strftime('%Y-%m-%d')
        start_year_str_split = self.start_date.split("-")
        start_year = int(start_year_str_split[0])
        end_year = int(self.end_date.split("-")[0])
        stk_date_list = []
        for this_year in range(start_year, end_year + 1):
            for this_date in report_date:
                start_date_str = start_year_str_split[1]+"-"+start_year_str_split[2]
                if this_year == start_year and this_date > start_date_str:
                    pass
                else:
                    date = self.cal.advance_date(str(this_year) + "-" + this_date, 0, 'd')
                    stk_date_list.append(date)

        flag = 0
        for date in stk_date_list:
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
