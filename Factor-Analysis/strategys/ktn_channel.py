from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
import talib


class KTNChannel(Strategy):
    atr_len = 20
    ma_len = 20
    band_width = 2
    
    
    def init(self):
        super().init()
        atr = talib.ATR(self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_len)
        
        self.sma = self.I(SMA, self.data.Close, self.ma_len)
        up_band = self.sma + self.band_width * atr
        down_band = self.sma - self.band_width * atr
        self.up_band = self.I(lambda x: up_band, 'up_band')
        self.down_band = self.I(lambda x: down_band, 'down_band')


    def next(self):
        super().next()
        if self.sma[-1] > self.sma[-2] and self.up_band[-1] <= self.data.High[-1]:
            self.buy()
        if self.sma[-1] < self.sma[-2] and self.down_band[-1] >= self.data.Low[-1]:
            for trade in self.trades:
                trade.close()
