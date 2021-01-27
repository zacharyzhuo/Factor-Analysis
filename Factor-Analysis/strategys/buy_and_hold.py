from backtesting import Backtest, Strategy


class BuyAndHold(Strategy):
    def set_param(self, buy_list, sell_list):
        self.buy_list = buy_list
        self.sell_list = sell_list


    def init(self):
        super().init()


    def next(self):
        super().next()
        today = self.data.index[-1].strftime('%Y-%m-%d')
        if today in self.buy_list:
            self.buy()
        elif today in self.sell_list:
          for trade in self.trades:
            trade.close()
