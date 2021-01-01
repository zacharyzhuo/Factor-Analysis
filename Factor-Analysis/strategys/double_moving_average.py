import numpy as np
import pandas as pd

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import talib


class DoubleMA(Strategy):
    n1 = 20
    n2 = 60
    
    def init(self):
        super().init()
        close = pd.Series(self.data.Close)
        sma1 = talib.SMA(close, timeperiod=self.n1)
        sma2 = talib.SMA(close, timeperiod=self.n2)
        
        self.sma1 = self.I(lambda x: sma1, 'sma1')
        self.sma2 = self.I(lambda x: sma2, 'sma2')

    def next(self):
        super().next()
        if (self.sma1 > self.sma2) & (self.sma1[-2] < self.sma2[-2]):
            self.buy(size=1000)
        elif (self.sma1 < self.sma2) & (self.sma1[-2] > self.sma2[-2]):
          for trade in self.trades:
              trade.close()
