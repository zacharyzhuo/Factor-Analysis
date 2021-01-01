import pandas as pd
import numpy as np
import datetime
import requests
import json

from backtesting import Backtest, Strategy

from strategys.ktnchannel import KTNChannel
from strategys.buyandhold import BuyAndHold


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

        self.set_ticker_data()
        self.allocate_equity()

    def set_ticker_data(self):
        self.ticker_list = ['4907', '6294', '5904', '4905', '6456']
        print('doing set_ticker_data...')
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
            stk_df.columns = ['Close', 'High', 'Low', 'Open', 'Volume']
            stk_df = stk_df.fillna(0).astype(int)
            output_dict[ticker] = stk_df
        self.ticker_data_dict = output_dict
        # print(self.ticker_data_dict)
    
    def allocate_equity(self):
        print('doing allocate_equity...')
        if self.weight_setting == "equal_weight":
            each_equity = self.start_equity / len(self.ticker_list)
            for ticker in self.ticker_list:
                self.ticker_equity_dict[ticker] = each_equity

        elif self.weight_setting == "equal_risk(ATR)":
            pass

        elif self.weight_setting == "equal_risk(SD)":
            pass
        print(self.ticker_equity_dict)
    
    def do_backtesting(self):
        print('doing do_backtesting...')
        for ticker in self.ticker_list:
            if self.strategy == "KTNChannel":
                bt = Backtest(self.ticker_data_dict[ticker],
                              KTNChannel,
                              cash=int(self.ticker_equity_dict[ticker]),
                              commission=0.0005,
                              exclusive_orders=True)
            elif self.strategy == "BuyAndHold":
                BuyAndHold.set_param(BuyAndHold, self.factor_name, ticker, self.cal)
                bt = Backtest(self.ticker_data_dict[ticker],
                              BuyAndHold,
                              cash=int(self.ticker_equity_dict[ticker]),
                              commission=0.0005,
                              exclusive_orders=True)
            output = bt.run()
            # bt.plot()
            # output._equity_curve.Equity.plot(use_index=False, logy=True)
            self.backtest_output_dict[ticker] = output
            print('Complete backtesting ', ticker)

    def proc_backtest_output(self):
        print('proc_backtest_output...')
        column_name = ['ticker', 'Start', 'End', 'Start Equity', 'Equity Final [$]', 'Net Profit',
                        'Return [%]', 'Return (Ann.) [%]', 'Volatility (Ann.) [%]', 'Sharpe Ratio', 
                        'Max. Drawdown [%]', '# Trades', 'Profit Factor', 'Profit', 'Loss',
                        '_equity_curve', '_trades_year', '_trades_pnl']
        output_list = []
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
            _equity_curve = value['_equity_curve']['Equity'].tolist()
            _equity_curve = " ".join(str(e) for e in _equity_curve)
            _trades_df = value['_trades']
            _trades_df['year'] = pd.DatetimeIndex(_trades_df['ExitTime']).year
            _trades_year = _trades_df['year'].tolist()
            _trades_year = " ".join(str(e) for e in _trades_year)
            _trades_pnl = _trades_df['PnL'].tolist()
            _trades_pnl = " ".join(str(e) for e in _trades_pnl)
            temp_list = [ticker, start, end, start_equity, final_equity, net_profit,
                            return_pct, ann_return_pct, ann_volatility_pct, sharpe_ratio, 
                            mdd_pct, trades, profit_factor, profit, loss, _equity_curve,
                            _trades_year, _trades_pnl]
            output_list.append(temp_list)
        output_df = pd.DataFrame(output_list, columns=column_name)
        output_df.to_csv('./data/result/output2.csv', header=True)
        print('complete backtest')
