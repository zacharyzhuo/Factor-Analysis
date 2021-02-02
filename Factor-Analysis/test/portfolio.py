import pandas as pd
import numpy as np
import datetime
import requests
import json
from backtesting import Backtest, Strategy

from strategy.ktn_channel import KTNChannel
from strategy.buy_and_hold import BuyAndHold


server_ip = "http://140.115.87.197:8090/"
commission = 0.0005


class Portfolio:
    def __init__(self, strategy_config, ticker_list, cal, fac):
        self.strategy_config = strategy_config
        self.ticker_list = ticker_list
        self.cal = cal
        self.fac = fac

        self.window_config = {}
        self.portfolio_performance_df = None
        self.portfolio_performance_dict = {}

        self.cal = cal
        self.fac = fac

        self.ticker_weight_dict = {}
        self.portfolio_performance_df = None
        self.portfolio_performance_dict = {}

        self._proc_backtest_output()


    def _set_stk_price_of_tickers(self):
        print('...Portfolio: _set_stk_price_of_tickers()...')
        start_date = self.strategy_config['start_date'].split("-")
        start_date = "".join(start_date)
        end_date = self.strategy_config['end_date'].split("-")
        end_date = "".join(end_date)
        payloads = {
            'ticker_list': self.ticker_list,
            'date': start_date + "-" + end_date
        }
        response = requests.get(server_ip + "stk/get_ticker_period_stk", params=payloads)
        output_dict = json.loads(response.text)['result']

        for ticker in self.ticker_list:
            stk_df = pd.DataFrame(output_dict[ticker])
            stk_df['date'] = [datetime.datetime.strptime(elm, "%Y-%m-%d") for elm in stk_df['date']]
            stk_df.set_index("date", inplace=True)
            stk_df.columns = ['Close', 'High', 'Low', 'Open', 'Volume', 'outstanding_share']
            stk_df = stk_df.drop('outstanding_share', axis=1)
            stk_df = stk_df.fillna(0).astype(int)
            output_dict[ticker] = stk_df
        return output_dict
    

    def _set_weight(self):
        print('...Portfolio: _set_weight()...')
        if self.strategy_config['weight_setting'] == 0:
            weight = self.strategy_config['start_equity'] / len(self.ticker_list)
            for ticker in self.ticker_list:
                self.ticker_weight_dict[ticker] = weight

        elif self.strategy_config['weight_setting'] == 1:
            pass

        elif self.strategy_config['weight_setting'] == 2:
            pass
    

    def _do_backtesting(self):
        stk_price_dict = self._set_stk_price_of_tickers()
        self._set_weight()
        print('...Portfolio: _do_backtesting()...')
        backtest_output_dict = {}
        for ticker in self.ticker_list:
            if self.strategy_config['strategy'] == 0:
                BuyAndHold.set_param(BuyAndHold, self.strategy_config['factor_list'][0], ticker, self.cal, self.fac)
                bt = Backtest(stk_price_dict[ticker],
                              BuyAndHold,
                              cash=int(self.ticker_weight_dict[ticker]),
                              commission=commission,
                              exclusive_orders=True)
            elif self.strategy_config['strategy'] == 1:
                bt = Backtest(stk_price_dict[ticker],
                              KTNChannel,
                              cash=int(self.ticker_weight_dict[ticker]),
                              commission=commission,
                              exclusive_orders=True)
            output = bt.run()
            # bt.plot()
            backtest_output_dict[ticker] = output
            print('Complete backtesting ', ticker)
        return backtest_output_dict


    def _proc_backtest_output(self):
        backtest_output_dict = self._do_backtesting()
        print('...Portfolio: _proc_backtest_output()...')
        column_name = ['ticker', 'Start', 'End', 'Start Equity', 'Equity Final [$]', 'Net Profit',
                        'Return [%]', 'Return (Ann.) [%]', 'Volatility (Ann.) [%]', 'Sharpe Ratio', 
                        'Max. Drawdown [%]', '# Trades', 'Profit Factor', 'Profit', 'Loss',]
        output_list = []
        output_dict = {}
        for index, value in backtest_output_dict.items():
            ticker = index
            start = value['Start']
            end = value['End']
            start_equity = self.ticker_weight_dict[index]
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
            # trades_df['year'] = pd.DatetimeIndex(trades_df['ExitTime']).year
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