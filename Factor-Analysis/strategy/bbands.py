from backtesting import Backtest, Strategy
from talib import BBANDS


class BBands(Strategy):

    def set_param(self, ma_len, band_width, start_date):
        self.ma_len = ma_len
        self.band_width = band_width
        self.start_date = start_date

    def init(self):
        super().init()
        
        up_band, mid, down_band = BBANDS(
            self.data.Close,
            timeperiod=self.ma_len,
            nbdevup=self.band_width,
            nbdevdn=self.band_width,
            matype=0
        )

        self.up_band = self.I(lambda x: up_band, 'up_band')
        self.mid = self.I(lambda x: mid, 'mid')
        self.down_band = self.I(lambda x: down_band, 'down_band')
        
    def next(self):
        super().next()
        today = self.data.index[-1].strftime('%Y-%m-%d')
        
        # 收盤價大於通道上軌: 買
        if self.data.Close > self.up_band:
            if not self.position:
                if today >= self.start_date:
                    self.buy()

        # 收盤價小於通道上軌: 賣
        if self.data.Close < self.down_band:
            if self.position:
                for trade in self.trades:
                    trade.close()
