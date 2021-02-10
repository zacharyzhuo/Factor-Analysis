from backtesting import Backtest, Strategy
from talib import BBANDS


class BBands(Strategy):

    ma_len = 20
    band_width = 2

    def init(self):
        super().init()
        up_band, mid, down_band = BBANDS(self.data.Close, timeperiod=self.ma_len, nbdevup=self.band_width, nbdevdn=self.band_width, matype=0)

        self.up_band = self.I(lambda x: up_band, 'up_band')
        self.mid = self.I(lambda x: mid, 'mid')
        self.down_band = self.I(lambda x: down_band, 'down_band')
        
    def next(self):
        super().next()
        # 收盤價大於通道上軌: 買
        if self.data.Close > self.up_band:
            if not self.position:
                self.buy()
        # 收盤價小於通道上軌: 賣
        if self.data.Close < self.down_band:
            if self.position:
                for trade in self.trades:
                    trade.close()
