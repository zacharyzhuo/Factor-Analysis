import pandas as pd
import numpy as np
import datetime
import requests
import json

from backtesting import Backtest, Strategy

from strategys.ktn_channel import KTNChannel
from strategys.buy_and_hold import BuyAndHold


server_ip = "http://140.115.87.197:8090/"


class Portfolio:
    def __init__(self, cal, strategy, optimization_setting, weight_setting, 
                factor_name, start_equity, start_date, end_date, ticker_list):
        self.cal = cal

        self.strategy = strategy
        self.optimization_setting = optimization_setting
        self.weight_setting = weight_setting
        self.factor_name = factor_name
        self.start_equity = start_equity
        self.start_date = start_date
        self.end_date = end_date
        self.ticker_list = ticker_list

        self.ticker_data_dict = {}
        self.ticker_equity_dict = {}
        self.backtest_output_dict = {}
        self.portfolio_performance_df = None
        self.portfolio_performance_dict = {}

        self.set_stk_price_of_tickers()
        self.allocate_equity()
        self.do_backtesting()
        self.proc_backtest_output()

    def set_stk_price_of_tickers(self):
        print('doing set_stk_price_of_tickers...')
        start_date = self.start_date.split("-")
        start_date = "".join(start_date)
        end_date = self.end_date.split("-")
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
        self.ticker_data_dict = output_dict
        # print(self.ticker_data_dict)
    
    def allocate_equity(self):
        print('doing allocate_equity...')
        if self.weight_setting == 0:
            each_equity = self.start_equity / len(self.ticker_list)
            for ticker in self.ticker_list:
                self.ticker_equity_dict[ticker] = each_equity

        elif self.weight_setting == 1:
            pass

        elif self.weight_setting == 2:
            pass
        print(self.ticker_equity_dict)
    
    def do_backtesting(self):
        print('doing do_backtesting...')
        for ticker in self.ticker_list:
            if self.strategy == 0:
                BuyAndHold.set_param(BuyAndHold, self.factor_name, ticker, self.cal)
                bt = Backtest(self.ticker_data_dict[ticker],
                              BuyAndHold,
                              cash=int(self.ticker_equity_dict[ticker]),
                              commission=0.0005,
                              exclusive_orders=True)
            elif self.strategy == 1:
                bt = Backtest(self.ticker_data_dict[ticker],
                              KTNChannel,
                              cash=int(self.ticker_equity_dict[ticker]),
                              commission=0.0005,
                              exclusive_orders=True)
            output = bt.run()
            # bt.plot()
            self.backtest_output_dict[ticker] = output
            print('Complete backtesting ', ticker)

    def proc_backtest_output(self):
        print('proc_backtest_output...')
        column_name = ['ticker', 'Start', 'End', 'Start Equity', 'Equity Final [$]', 'Net Profit',
                        'Return [%]', 'Return (Ann.) [%]', 'Volatility (Ann.) [%]', 'Sharpe Ratio', 
                        'Max. Drawdown [%]', '# Trades', 'Profit Factor', 'Profit', 'Loss',]
        output_list = []
        output_dict = {}
        for index, value in self.backtest_output_dict.items():
            ticker = index
            start = value['Start']
            end = value['End']
            start_equity = self.ticker_equity_dict[index]
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
            trades_df['year'] = pd.DatetimeIndex(trades_df['ExitTime']).year
            trades_df = trades_df[['PnL', 'year']]
            trades_df = trades_df.set_index('year')
            trades_dict = trades_df.to_dict()
            self.portfolio_performance_dict[ticker] = {'equity_curve': equity_curve_dict, 'trades': trades_dict}

            temp_list = [ticker, start, end, start_equity, final_equity, net_profit,
                            return_pct, ann_return_pct, ann_volatility_pct, sharpe_ratio, 
                            mdd_pct, trades, profit_factor, profit, loss]
            output_list.append(temp_list)
        self.portfolio_performance_df = pd.DataFrame(output_list, columns=column_name)
        self.portfolio_performance_df = self.portfolio_performance_df.set_index('ticker')
        print('complete processing portfolio output')
