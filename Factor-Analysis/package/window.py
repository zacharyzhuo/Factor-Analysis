import pandas as pd
from utils.config import Config
from package.backtest_handler import BacktestHandler


class Window:

    def __init__(self, window_config, t2_period, cal, fac):
        self.window_config = window_config
        self._t2_period = t2_period
        self._cal = cal
        self._fac = fac
        self._n_season = window_config['n_season']

        self._cfg = Config()
        self._backtest_handler = BacktestHandler(window_config, cal, fac)
        self._group_ticker = []
        self._start_equity = 0

        self._play_t1(t2_period[0])
        self._play_t2()
    
    # T1: 選股
    def _play_t1(self, date):
        if self.window_config['is_first'] == True:
            date = self._cal.get_trade_date(date, -2, 's')
        else:
            date = self._cal.get_trade_date(date, -1, 's')

        factor_df_dict = {}

        # 抓因子資料
        for factor in self.window_config['factor']:
            factor_all_date_df = self._fac.factor_df_dict[factor]
            factor_df = factor_all_date_df.loc[date].to_frame()

            # 如果要多看前幾季的因子
            if self._n_season > 0:
                for i in range(self._n_season):
                    date = self._cal.get_trade_date(date, 1, 's')
                    temp_factor_df = factor_all_date_df.loc[date]
                    factor_df = factor_df.join(temp_factor_df)
                # 將這幾季的因子取平均
                factor_df['mean'] = factor_df.mean(axis=1)
                factor_df = factor_df['mean']
            factor_df = factor_df.rename(columns={factor_df.columns[0] : factor})
            factor_df_dict[factor] = factor_df

        self.window_config['factor_data'] = factor_df_dict

        # 單因子
        if len(self.window_config['factor']) == 1:
            factor = self.window_config['factor'][0]
            # 依照該因子排序全部標的
            group_list = self._fac.rank_factor(factor_df_dict[factor], factor)
            # 選出該群的標的
            the_group_df = group_list[self.window_config['group'] - 1]
        
        # 雙因子
        elif len(self.window_config['factor']) == 2:
            first_factor = self.window_config['factor'][0]
            second_factor = self.window_config['factor'][1]

            # 先以第一個因子排序
            group_list = self._fac.rank_factor(factor_df_dict[first_factor], first_factor)
            # 選出該群的標的
            the_group_ticker_list = group_list[self.window_config['group'] - 1]['ticker'].tolist()
            # 抓出這群所有標的 第二個因子的資料
            second_fac_group_df = factor_df_dict[second_factor].loc[the_group_ticker_list]
            # 用第二個因子資料再排名一次這群標的
            the_group_df = self._fac.rank_factor(second_fac_group_df, second_factor)[0]
        
        self._group_ticker = the_group_df['ticker'].tolist()

        # 固定參數
        if self.window_config['strategy'] == 0 or self.window_config['window'] == 0:
            self._backtest_handler.group_ticker = self._group_ticker

        # 定錨
        elif self.window_config['window'] == 1:
            # 傳入窗格長度
            opt_ref_peroid = int(self._cfg.get_value('parameter', 'opt_ref_peroid'))
            start_date = self.window_config['start_date']
            t1_start = self._cal.get_trade_date(start_date, opt_ref_peroid*-1, 'm')
            t1_end = self._t2_period[0]
            self._backtest_handler.t1_optimize([t1_start, t1_end], self._group_ticker)

        # 非定錨
        elif self.window_config['window'] == 2:
            # 傳入窗格長度
            opt_ref_peroid = int(self._cfg.get_value('parameter', 'opt_ref_peroid'))
            t1_start = self._cal.get_trade_date(self._t2_period[0], opt_ref_peroid*-1, 'm')
            t1_end = self._t2_period[0]
            self._backtest_handler.t1_optimize([t1_start, t1_end], self._group_ticker)

    # T2: 買進T1選的股 回測 記錄績效
    def _play_t2(self):
        self._backtest_handler.t2_backtest(self._t2_period)

        self.window_config = self._backtest_handler.window_config
        
        # 更新投組目前的現金
        self.window_config['cash'] = self.window_config['portfolio_equity'].iloc[-1]['total']

        if self.window_config['is_first'] == True:
            self.window_config['is_first'] = False
