from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
from talib import BBANDS


class BBands(Strategy):
    atr_len = 20
    ma_len = 20
    band_width = 2
    
    
    def init(self):
        super().init()
        up, mid, low = BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)


    def next(self):
        super().next()
        if self.sma[-1] > self.sma[-2] and self.up_band[-1] <= self.data.High[-1]:
            self.buy()
        if self.sma[-1] < self.sma[-2] and self.down_band[-1] >= self.data.Low[-1]:
            for trade in self.trades:
                trade.close()
