import pandas as pd
import numpy as np
import datetime
import requests
import json
from backtesting import Backtest, Strategy

from modules.sliding_window import SlidingWindow
from strategys.one_factor_window import OneFactorWindow
from strategys.two_factor_window import TwoFactorWindow
from strategys.buy_and_hold import BuyAndHold
from strategys.bbands import BBands


server_ip = "http://140.115.87.197:8090/"
commission = 0.005


class Portfolio:
    def __init__(self, strategy_config, cal, fac):
        self.strategy_config = strategy_config
        self.cal = cal
        self.fac = fac

        self.window_config = {
            'strategy': strategy_config['strategy'],
            'factor_list': strategy_config['factor_list'],
            'n_season': strategy_config['n_season'],
            'group': strategy_config['group'],
            'position': strategy_config['position'],
            'start_date': strategy_config['start_date'],
            'end_date': strategy_config['end_date'],
            'if_first': True,
            'ticker_list': [],
            'signal': {},
            'weight': {},
        }
        self.portfolio_performance_df = None
        self.portfolio_performance_dict = {}

        # if strategy_config['strategy'] != 2:
        #     self._create_sliding_window()
        #     self._proc_signal()
        # else:
        #     self._create_bbands_strategy()
        
        # stk_price_dict = self._get_stk_price()
        # self._set_weight()
        # backtest_result_dict = self._do_backtesting(stk_price_dict)
        # self._proc_backtest_result(backtest_result_dict)

        self._create_sliding_window()
        if strategy_config['strategy'] != 2:
            self._proc_signal()
        stk_price_dict = self._get_stk_price()
        self._set_weight()
        backtest_result_dict = self._do_backtesting(stk_price_dict)
        self._proc_backtest_result(backtest_result_dict)


    def _create_sliding_window(self):
        print('...Portfolio: _create_sliding_window()...')
        strategy_config = self.strategy_config
        window_config = self.window_config
        
        sliding_window = SlidingWindow(window_config, self.cal, self.fac)
        self.window_config = sliding_window.window_config


    # def _create_bbands_strategy(self):
    #     print('...Portfolio: _create_bbands_strategy()...')
    #     strategy_config = self.strategy_config
    #     window_config = self.window_config
    #     report_date = self.cal.get_report_date_list(window_config['start_date'], window_config['end_date'])[0]

    #     if len(strategy_config['factor_list']) == 1:
    #         my_window = OneFactorWindow(window_config, report_date, self.cal, self.fac)
    #         window_config['ticker_list'] = my_window.get_ticker_list()
    #     elif len(strategy_config['factor_list']) == 2:
    #         my_window = TwoFactorWindow(window_config, report_date, self.cal, self.fac)
    #         window_config['ticker_list'] = my_window.get_ticker_list()
    #     self.window_config = window_config


    def _get_stk_price(self):
        print('...Portfolio: _get_stk_price()...')
        strategy_config = self.strategy_config
        ticker_list = self.window_config['ticker_list']
        start_date = strategy_config['start_date'].split("-")
        start_date = "".join(start_date)
        end_date = strategy_config['end_date'].split("-")
        end_date = "".join(end_date)
        payloads = {
            'ticker_list': ticker_list,
            'date': start_date + "-" + end_date
        }
        response = requests.get(server_ip + "stk/get_ticker_period_stk", params=payloads)
        result_dict = json.loads(response.text)['result']

        for ticker in ticker_list:
            stk_df = pd.DataFrame(result_dict[ticker])
            stk_df['date'] = [datetime.datetime.strptime(elm, "%Y-%m-%d") for elm in stk_df['date']]
            stk_df.set_index("date", inplace=True)
            stk_df.columns = ['Close', 'High', 'Low', 'Open', 'Volume', 'outstanding_share']
            stk_df = stk_df.drop('outstanding_share', axis=1)
            # stk_df = stk_df.interpolate(method='linear', limit_direction='forward', axis=0)
            stk_df = stk_df.dropna()
            result_dict[ticker] = stk_df
        return result_dict
    

    def _set_weight(self):
        print('...Portfolio: _set_weight()...')
        strategy_config = self.strategy_config
        ticker_list = self.window_config['ticker_list']
        weight = strategy_config['start_equity'] / len(ticker_list)
        for ticker in ticker_list:
            self.window_config['weight'][ticker] = weight
    

    def _proc_signal(self):
        print('...Portfolio: _proc_signal()...')
        signal_dict = self.window_config['signal']
        buy_and_sell_dict = {}
        for ticker in self.window_config['ticker_list']:
            temp_dict = {}
            temp_dict['buy_list'] = []
            temp_dict['sell_list'] = []
            buy_and_sell_dict[ticker] = temp_dict

        for date, value in signal_dict.items():
            for ticker, signal in value.items():
                if signal == 1:
                    buy_and_sell_dict[ticker]['buy_list'].append(date)
                elif signal == 3:
                    buy_and_sell_dict[ticker]['sell_list'].append(date)
        # print(buy_and_sell_dict)
        self.window_config['buy_and_sell_list'] = buy_and_sell_dict


    def _do_backtesting(self, stk_price_dict):
        print('...Portfolio: _do_backtesting()...')
        strategy_config = self.strategy_config
        window_config = self.window_config
        backtest_result_dict = {}

        if strategy_config['strategy'] != 2:
            for ticker, value in window_config['buy_and_sell_list'].items():
                try:
                    buy_list = value['buy_list']
                    sell_list = value['sell_list']
                    BuyAndHold.set_param(BuyAndHold, buy_list, sell_list)
                    bt = Backtest(stk_price_dict[ticker],
                                    BuyAndHold,
                                    cash=int(window_config['weight'][ticker]),
                                    commission=commission,
                                    exclusive_orders=True)
                    result = bt.run()
                    # bt.plot()
                    backtest_result_dict[ticker] = result
                    print('Complete backtesting ', ticker)
                except Exception as e:
                    print(e)
                    print('Fail: ', ticker)
                    pass
        else:
            for ticker in window_config['ticker_list']:
                try:
                    BBands.set_param(BBands, window_config['signal'])
                    bt = Backtest(stk_price_dict[ticker],
                                    BBands,
                                    cash=int(window_config['weight'][ticker]),
                                    commission=commission,
                                    exclusive_orders=True)
                    result = bt.run()
                    result = bt.optimize(ma_len=range(5, 50, 5), band_width=list(np.arange(0.1, 2.0, 0.1)))
                    # print(result._strategy)
                    # bt.plot()
                    backtest_result_dict[ticker] = result
                    print('Complete backtesting ', ticker)
                except Exception as e:
                    print(e)
                    print('Fail: ', ticker)
                    pass
        return backtest_result_dict


    def _proc_backtest_result(self, backtest_result_dict):
        print('...Portfolio: _proc_backtest_result()...')
        window_config = self.window_config
        column_name = ['ticker', 'Start', 'End', 'Start Equity', 'Equity Final [$]', 'Net Profit',
                        'Return [%]', 'Return (Ann.) [%]', 'Volatility (Ann.) [%]', 'Sharpe Ratio', 
                        'Max. Drawdown [%]', '# Trades', 'Profit Factor', 'Profit', 'Loss',]
        result_list = []
        result_dict = {}
        for ticker, value in backtest_result_dict.items():
            start = value['Start']
            end = value['End']
            start_equity = window_config['weight'][ticker]
            final_equity = value['Equity Final [$]']
            net_profit = final_equity - start_equity
            return_pct = value['Return [%]']
            ann_return_pct = value['Return (Ann.) [%]']
            ann_volatility_pct = value['Volatility (Ann.) [%]']
            sharpe_ratio = value['Sharpe Ratio']
            mdd_pct = value['Max. Drawdown [%]']
            trades = value['# Trades']
            profit_factor = value['Profit Factor']
            trades_pnl_df = value['_trades']['PnL']
            profit = trades_pnl_df[trades_pnl_df >= 0].sum()
            loss = trades_pnl_df[trades_pnl_df < 0].sum()

            equity_curve_df = value['_equity_curve'][['Equity']]
            equity_curve_df.index.name = 'date'
            equity_curve_df = equity_curve_df.reset_index()
            equity_curve_df['date'] = equity_curve_df['date'].dt.strftime('%Y-%m-%d')
            equity_curve_df = equity_curve_df.set_index('date')
            equity_curve_dict = equity_curve_df.to_dict()

            trades_df = value['_trades']
            if not trades_df.empty:
                trades_df['EntryTime'] = trades_df['EntryTime'].dt.strftime('%Y-%m-%d')
                trades_df['ExitTime'] = trades_df['ExitTime'].dt.strftime('%Y-%m-%d')
            trades_df = trades_df[['PnL', 'EntryTime', 'ExitTime']]
            trades_dict = trades_df.to_dict()
            self.portfolio_performance_dict[ticker] = {'equity_curve': equity_curve_dict, 'trades': trades_dict}

            temp_list = [ticker, start, end, start_equity, final_equity, net_profit,
                            return_pct, ann_return_pct, ann_volatility_pct, sharpe_ratio, 
                            mdd_pct, trades, profit_factor, profit, loss]
            result_list.append(temp_list)
        self.portfolio_performance_df = pd.DataFrame(result_list, columns=column_name)
        self.portfolio_performance_df = self.portfolio_performance_df.set_index('ticker')
