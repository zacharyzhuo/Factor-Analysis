from backtesting import Backtest, Strategy
from talib import BBANDS


class BBandsWindow(Strategy):

    ma_len = 20
    band_width = 2
    signal = -1
    
    def set_param(self, signal_dict):
        self._signal_dict = signal_dict

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

        # 每次T2開始的日子
        if today in self._signal_dict:
            self.signal = self._signal_dict[today]
            # 目前還持有部位且當這個T2的訊號為賣出時則全部賣出
            if self.signal == 3 and self.position:
                for trade in self.trades:
                    trade.close()

        # 只有buy&hold可以買賣
        if self.signal == 1 or self.signal == 2:
            if self.data.Close > self.up_band:
                if not self.position:
                    self.buy()
            if self.data.Close < self.down_band:
                if self.position:
                    for trade in self.trades:
                        trade.close()
