import pandas as pd
import numpy as np
import datetime
import requests
import json

import matplotlib.pyplot as plt


# strategy = [0, 1, 2]
# factor_list = ['GVI', 'EPS', 'MOM', 'PE', 'EV_EBITDA', 'EV_S', 'FC_P', 'CROIC', 'FC_OI', 'FC_LTD']
# 0: equal_weight; 1: equal_risk(ATR); 2: equal_risk(SD)
# weight_setting = [0, 1, 2]                  
# n_season = [1, 2]
group = [1, 2, 3, 4, 5, 6]
position = [5, 10, 15, 30, 90]

risk_free_rate = 0.01


class Analysis:
    def __init__(self, start_equity, start_date, end_date):
        self.start_equity = start_equity
        self.start_date = start_date
        self.end_date = end_date
        
        self.df = None
        self.equtiy_df = None
        self.trades_df = None
        # self._read_output_file()


    def _read_output_file(self, strategy, factor, weight_setting, n_season, group, position):
        print('...Analysis: doing _read_output_file()...')
        path = './portfolio_performance/'+factor+'/'
        file_name = "%s_%s_%s_%s_%s_%s" % (str(strategy),
                                    factor, 
                                    str(weight_setting), 
                                    str(n_season), 
                                    str(group), 
                                    str(position))
        # print('file_name: ', file_name)
        self.df = pd.read_csv(path+file_name+'.csv')

        with open(path+file_name+'.json', 'r') as file:
            data_dict = json.load(file)

        equtiy_dict = {}
        trades_dict = {}
        for ticker, value in data_dict.items():
            equtiy_dict[ticker] = value['equity_curve']['Equity']
            trades_dict[ticker] = value['trades']

        equity_list = []
        for ticker, value in equtiy_dict.items():
            equity_df = pd.DataFrame.from_dict(value, orient='index', columns=[ticker])
            equity_list.append(equity_df)
        equity_df = pd.concat(equity_list, axis=1)
        equity_df.index.name = 'date'
        equity_df['total_equity']=equity_df.iloc[:, -5:].sum(axis=1)
        self.equity_df = equity_df

        year_list = range(int(self.start_date.split('-')[0]), int(self.end_date.split('-')[0]) + 1)
        self.trades_df = pd.DataFrame(year_list, columns=['year'])
        for ticker, value in trades_dict.items():
            del value['EntryTime']
            ticker_trades_df = pd.DataFrame(value)
            ticker_trades_df.columns = [ticker, 'year']
            ticker_trades_df['year'] = ticker_trades_df['year'].apply(lambda x: x.split('-')[0]).astype(int)
            ticker_trades_df = ticker_trades_df.groupby('year').sum()
            self.trades_df = self.trades_df.merge(ticker_trades_df, on='year', how='outer')

        self.trades_df['total_net_profit'] = self.trades_df.iloc[:, -5:].sum(axis=1)
        # print("total_net_profit: ", self.trades_df['total_net_profit'].sum())
        self.trades_df = self.trades_df.set_index('year')
        return file_name


    def analysis_factor_performance(self, strategy, factor):
        weight_setting = 0
        n_season = 0
        df_list = []
        for gro in group:
            for pos in position:
                file_name = self._read_output_file(strategy, factor, weight_setting, n_season, gro, pos)
                porfolio_performance_list = self.anslysis_portfolio()
                porfolio_performance_list.insert(0, file_name)
                df_list.append(porfolio_performance_list)
        column_name = ['file_name', 'Net Profit (%)', 'CAGR (%)', 'MDD (%)', 'Profit Factor', 'Standar Error', 'Sharp Ratio']
        df = pd.DataFrame(df_list, columns=column_name)
        print(df)


    def anslysis_portfolio(self):
        print('...Analysis: doing anslysis_portfolio()...')
        df = self.df
        equity_df = self.equity_df
        porfolio_performance_list = []

        # Net Profit
        final_equity = df['Equity Final [$]'].sum()
        net_profit_rate = (final_equity - self.start_equity) / self.start_equity * 100
        # print("net_profit: ", final_equity - self.start_equity)
        porfolio_performance_list.append(net_profit_rate)

        # CAGR
        start_date_list = self.start_date.split("-")
        end_date_list = self.end_date.split("-")
        if end_date_list[1] == "1" and end_date_list[2] == "1":
            n = int(end_date_list[0]) - int(start_date_list[0])
        else:
            n = int(end_date_list[0]) - int(start_date_list[0]) + 1
        cagr = ((final_equity / self.start_equity) ** (1/n) - 1) * 100
        porfolio_performance_list.append(cagr)

        # MDD
        mdd = df['Max. Drawdown [%]'].min()
        porfolio_performance_list.append(mdd)

        # Profit Factor
        total_profit = df['Profit'].sum()
        total_loss = df['Loss'].sum()
        profit_factor = total_profit / total_loss * -1
        porfolio_performance_list.append(profit_factor)

        # Standar Error
        standar_error = equity_df['total_equity'].std(axis = 0, skipna = True)
        porfolio_performance_list.append(standar_error)

        # Sharp Ratio
        sharp_ratio = (df['Return [%]'].mean() - (risk_free_rate * 100)) / standar_error
        porfolio_performance_list.append(sharp_ratio)

        column_name = ['Net Profit (%)', 'CAGR (%)', 'MDD (%)', 'Profit Factor', 'Standar Error', 'Sharp Ratio']
        porfolio_performance_list = [round(x, 2) for x in porfolio_performance_list]
        porfolio_performance_df = pd.DataFrame([porfolio_performance_list], columns=column_name)
        # print(porfolio_performance_df.T)
        return porfolio_performance_list


    def rank_portfolio_return(self):
        print('...Analysis: doing rank_portfolio_return()...')
        df = self.df
        portfolio_return_df = df.sort_values(ascending=False, by='Return [%]')
        portfolio_return_df = portfolio_return_df.reset_index(drop=True)
        portfolio_return_df = portfolio_return_df[['ticker', 'Return [%]', '# Trades']]
        print(portfolio_return_df)


    def plot_net_profit_years(self):
        print('...Analysis: doing plot_net_profit_years()...')
        equity_df = self.equity_df
        trades_df = self.trades_df

        equity_df = equity_df.reset_index()
        equity_df['year'] = equity_df['date'].apply(lambda x: x.split('-')[0])
        year_list = range(int(self.start_date.split('-')[0]), int(self.end_date.split('-')[0])+1)
        start_equity_list = []
        for year in year_list:
            this_year_df = equity_df.loc[equity_df['year'] == str(year)]
            start_equity_of_first_day = this_year_df['total_equity'].iloc[0]
            start_equity_list.append(start_equity_of_first_day)

        trades_df['start_equity'] = start_equity_list
        trades_df['net_profit_rate'] = trades_df['total_net_profit']/trades_df['start_equity']*100
        
        color_list = []
        for i in range(len(trades_df['net_profit_rate'])):
            if trades_df['net_profit_rate'].iloc[i] >= 0:
                color_list.append('r')
            else:
                color_list.append('g')
        ax = trades_df['net_profit_rate'].plot(kind="bar", color=color_list)
        ax.set_xlabel("Year")
        ax.set_ylabel("Net Profit (%)")
        plt.show()
