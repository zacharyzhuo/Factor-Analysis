import pandas as pd
import numpy as np
import datetime
import requests
import json

import matplotlib.pyplot as plt 

class Analysis:
    def __init__(self, start_equity, start_date, end_date, risk_free_rate):
        self.start_equity = start_equity
        self.start_date = start_date
        self.end_date = end_date
        self.risk_free_rate = risk_free_rate
        
        self.df = None
        self.equity_df = None
        self.read_output_csv()
        self.anslysis_portfolio()
        self.rank_portfolio_return()
        self.plot_net_profit_years()

    def read_output_csv(self):
        print('doing read_output_csv()...')
        self.df = pd.read_csv('./data/result/output.csv')

    def anslysis_portfolio(self):
        print('doing anslysis_portfolio()...')
        df = self.df
        porfolio_performance_list = []
        # Net Profit
        final_equity = df['Equity Final [$]'].sum()
        net_profit = self.start_equity - final_equity
        porfolio_performance_list.append(net_profit)
        # CAGR
        start_date_list = self.start_date.split("-")
        end_date_list = self.end_date.split("-")
        if end_date_list[1] == "1" and end_date_list[2] == "1":
            n = int(end_date_list[0]) - int(start_date_list[0])
        else:
            n = int(end_date_list[0]) - int(start_date_list[0]) + 1
        cagr = (final_equity/self.start_equity) ** (1/n) - 1
        porfolio_performance_list.append(cagr)
        # MDD
        mdd = df['Max. Drawdown [%]'].min()
        porfolio_performance_list.append(mdd)
        # Profit Factor
        total_profit = df['Profit'].sum()
        total_loss = df['Loss'].sum()
        profit_factor = total_profit / total_loss
        porfolio_performance_list.append(profit_factor)
        # Standar Error
        equity_list = []
        for value in df['_equity_curve']:
            ticker_equity_list = [float(x) for x in value.split(" ")]
            ticker_equity_ser = pd.Series(ticker_equity_list)
            equity_list.append(ticker_equity_ser)
        equity_df = pd.concat(equity_list, axis=1)
        equity_df['total_equity']=equity_df.iloc[:, -5:].sum(axis=1)
        self.equity_df = equity_df
        standar_error = equity_df['total_equity'].std(axis = 0, skipna = True)
        porfolio_performance_list.append(standar_error)
        # Sharp Ratio
        sharp_ratio = (df['Return [%]'].mean() - (self.risk_free_rate * 100)) / standar_error
        porfolio_performance_list.append(sharp_ratio)

        column_name = ['Net Profit', 'CAGR', 'MDD', 'Profit Factor', 'Standar Error', 'Sharp Ratio']
        porfolio_performance_df = pd.DataFrame([porfolio_performance_list], columns=column_name)
        print(porfolio_performance_df.T)

    def rank_portfolio_return(self):
        print('doing rank_portfolio_return()...')
        df = self.df
        portfolio_return_df = df.sort_values(ascending=False, by='Return [%]')
        portfolio_return_df = portfolio_return_df.reset_index(drop=True)
        portfolio_return_df = portfolio_return_df[['ticker', 'Return [%]', '# Trades']]
        print(portfolio_return_df)

    def plot_net_profit_years(self):
        print('doing plot_net_profit_years()...')
        df = self.df
        year_list = range(int(self.start_date.split('-')[0]), int(self.end_date.split('-')[0]) + 1)
        pofolio_net_profit_df = pd.DataFrame(year_list, columns=['year'])
        for i in range(len(df)):
            ticker_trades_year = df['_trades_year'].iloc[i]
            ticker_trades_year_list = [int(x) for x in ticker_trades_year.split(" ")]
            ticker_trades_pnl = df['_trades_pnl'].iloc[i]
            ticker_trades_pnl_list = [float(x) for x in ticker_trades_pnl.split(" ")]
            ticker_trades_df = pd.DataFrame({'year': ticker_trades_year_list, i: ticker_trades_pnl_list})
            ticker_trades_df = ticker_trades_df.groupby('year').sum()
            pofolio_net_profit_df = pofolio_net_profit_df.merge(ticker_trades_df, on='year', how='outer')

        pofolio_net_profit_df['total_net_profit'] = pofolio_net_profit_df.iloc[:, -5:].sum(axis=1)
        pofolio_net_profit_df = pofolio_net_profit_df.set_index('year')
        print(pofolio_net_profit_df)
        print('@@@@@')
        print()

        color_list = []
        for i in range(len(pofolio_net_profit_df['total_net_profit'])):
            if pofolio_net_profit_df['total_net_profit'].iloc[i] >= 0:
                color_list.append('r')
            else:
                color_list.append('g')
        bar_list = pofolio_net_profit_df['total_net_profit'].plot(kind="bar", figsize=(9,8), color=color_list)
        plt.show()
