import pandas as pd
import numpy as np
import datetime
import requests
import json
from backtesting import Backtest, Strategy

from modules.sliding_window import SlidingWindow
from strategys.one_factor_window import OneFactorWindow
from strategys.two_factor_window import TwoFactorWindow
from strategys.my_backtest import MyBacktest
from strategys.bbands import BBands


server_ip = "http://140.115.87.197:8090/"
commission = 0.0005
# 1: one factor; 2: two factor
pick_ticker_method = [1, 2]


class Portfolio:
    def __init__(self, strategy_config, cal, fac):
        self.strategy_config = strategy_config
        self.cal = cal
        self.fac = fac

        self.window_config = {}
        self.portfolio_performance_df = None
        self.portfolio_performance_dict = {}

        if strategy_config['strategy'] != 2:
            self._create_sliding_window()
            stk_price_dict = self._get_stk_price()
            self._set_weight()
            self._proc_signal()
            backtest_output_dict = self._do_backtesting(stk_price_dict)
            self._proc_backtest_output(backtest_output_dict)
        else:
            self._create_bbands_strategy()


    def _create_sliding_window(self):
        print('...Portfolio: _create_sliding_window()...')
        strategy_config = self.strategy_config
        window_config = {
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
        sliding_window = SlidingWindow(window_config, self.cal, self.fac)
        self.window_config = sliding_window.window_config


    def _create_bbands_strategy(self):
        print('...Portfolio: _create_bbands_strategy()...')
        strategy_config = self.strategy_config
        window_config = {
            'strategy': strategy_config['strategy'],
            'factor_list': strategy_config['factor_list'],
            'pick_ticker_method': pick_ticker_method[0],
            'n_season': strategy_config['n_season'],
            'group': strategy_config['group'],
            'position': strategy_config['position'],
            'start_date': strategy_config['start_date'],
            'end_date': strategy_config['end_date'],
            'ticker_list': [],
            'weight': {},
        }
        report_date = self.cal.get_report_date_list(window_config['start_date'], window_config['end_date'])[0]

        if window_config['pick_ticker_method'] == 1:
            one_factor_window = OneFactorWindow(window_config, report_date, self.cal, self.fac)
            window_config['ticker_list'] = one_factor_window.get_ticker_list()
        elif window_config['pick_ticker_method'] == 2:
            two_factor_window = TwoFactorWindow(window_config, report_date, self.cal, self.fac)
            window_config['ticker_list'] = two_factor_window.get_ticker_list()
        self.window_config = window_config

        stk_price_dict = self._get_stk_price()
        self._set_weight()

        print(self.window_config)


    def _proc_ticker_list(self):
        print('...Portfolio: _proc_ticker_list()...')


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
        output_dict = json.loads(response.text)['result']

        for ticker in ticker_list:
            stk_df = pd.DataFrame(output_dict[ticker])
            stk_df['date'] = [datetime.datetime.strptime(elm, "%Y-%m-%d") for elm in stk_df['date']]
            stk_df.set_index("date", inplace=True)
            stk_df.columns = ['Close', 'High', 'Low', 'Open', 'Volume', 'outstanding_share']
            stk_df = stk_df.drop('outstanding_share', axis=1)
            stk_df = stk_df.interpolate()
            output_dict[ticker] = stk_df
        return output_dict
    

    def _set_weight(self):
        print('...Portfolio: _set_weight()...')
        strategy_config = self.strategy_config
        ticker_list = self.window_config['ticker_list']
        if strategy_config['weight_setting'] == 0:
            weight = strategy_config['start_equity'] / len(ticker_list)
            for ticker in ticker_list:
                self.window_config['weight'][ticker] = weight

        elif strategy_config['weight_setting'] == 1:
            pass

        elif strategy_config['weight_setting'] == 2:
            pass
    

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
        backtest_output_dict = {}

        if strategy_config['strategy'] != 2:
            for ticker, value in window_config['buy_and_sell_list'].items():
                try:
                    buy_list = value['buy_list']
                    sell_list = value['sell_list']
                    MyBacktest.set_param(MyBacktest, buy_list, sell_list)
                    bt = Backtest(stk_price_dict[ticker],
                                    MyBacktest,
                                    cash=int(window_config['weight'][ticker]),
                                    commission=commission,
                                    exclusive_orders=True)
                    output = bt.run()
                    # bt.plot()
                    backtest_output_dict[ticker] = output
                    print('Complete backtesting ', ticker)
                except Exception as e:
                    print(e)
                    print('Fail: ', ticker)
                    pass
        else:
            for ticker in window_config['ticker_list']:
                try:
                    bt = Backtest(stk_price_dict[ticker],
                                    BBands,
                                    cash=int(window_config['weight'][ticker]),
                                    commission=commission,
                                    exclusive_orders=True)
                    output = bt.run()
                    # bt.plot()
                    backtest_output_dict[ticker] = output
                    print('Complete backtesting ', ticker)
                except Exception as e:
                    print(e)
                    print('Fail: ', ticker)
                    pass
        return backtest_output_dict


    def _proc_backtest_output(self, backtest_output_dict):
        print('...Portfolio: _proc_backtest_output()...')
        window_config = self.window_config
        column_name = ['ticker', 'Start', 'End', 'Start Equity', 'Equity Final [$]', 'Net Profit',
                        'Return [%]', 'Return (Ann.) [%]', 'Volatility (Ann.) [%]', 'Sharpe Ratio', 
                        'Max. Drawdown [%]', '# Trades', 'Profit Factor', 'Profit', 'Loss',]
        output_list = []
        output_dict = {}
        for ticker, value in backtest_output_dict.items():
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
            output_list.append(temp_list)
        self.portfolio_performance_df = pd.DataFrame(output_list, columns=column_name)
        self.portfolio_performance_df = self.portfolio_performance_df.set_index('ticker')
