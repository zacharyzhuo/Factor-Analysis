import pandas as pd
import numpy as np
import datetime
import requests
import json

from modules.calendar import Calendar
from modules.factor import Factor
from modules.portfolio import Portfolio


strategy = [0, 1]                           # 0: BuyAndHold; 1: KTNChannel
optimization_setting = [0, 1]               # 0: 無變數(or單一變數); 1: 最佳化變數
weight_setting = [0, 1, 2]                  # 0: equal_weight; 1: equal_risk(ATR); 2: equal_risk(SD)
factor_name = ['GVI', 'EPS', 'MOM', 'PE', 'EV_EBITDA', 'EV_S', 'FC_P', 'CROIC', 'FC_OI', 'FC_LTD']
group = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
position = [5, 10, 15, 30, 90, 150]


class MyStrategy:
    def __init__(self, strategy, optimization_setting, weight_setting, factor_name,
                group, position, start_equity, start_date, end_date):
        self.strategy = strategy
        self.optimization_setting = optimization_setting
        self.weight_setting = weight_setting
        self.factor_name = factor_name
        self.group = group
        self.position = position
        self.start_equity = start_equity
        self.start_date = start_date
        self.end_date = end_date
        
        self.cal = Calendar('TW')
        self.portfolio = None

        self.create_portfolio()
        self.write_portfolio_performance()
    
    def get_ticker_list(self):
        print('doing get_ticker_list...')
        date = self.cal.advance_date(self.start_date, 1, 's')
        print('backtesting period: ' + self.start_date + ' to ' + self.end_date)
        print('get factor data at ' + date)
        self.factor = Factor(self.factor_name, date)
        print(self.factor.factor_df)
        ranking_list = self.factor.rank_factor()
        print('get group ' + str(self.group) + ' from ranking list')
        ticker_group_df = ranking_list[self.group - 1]
        print(ticker_group_df)
        print('get a ticker list of top ' + str(self.position) + ' from group ' + str(self.group))
        ticker_list = ticker_group_df['ticker'].iloc[0: self.position].tolist()
        print('ticker_list: ', ticker_list)
        return ticker_list
    
    def create_portfolio(self):
        print('doing create_portfolio...')
        ticker_list = self.get_ticker_list()
        self.portfolio = Portfolio(self.cal,
                                   self.strategy,
                                   self.optimization_setting,
                                   self.weight_setting,
                                   self.factor_name,
                                   self.start_equity,
                                   self.start_date,
                                   self.end_date,
                                   ticker_list)
    
    def write_portfolio_performance(self):
        print('doing write_portfolio_performance...')
        portfo_df = self.portfolio.portfolio_performance_df
        portfo_dict = self.portfolio.portfolio_performance_dict

        file_name = ""
        if self.strategy == 0:
            file_name += "B&H"
            path_stra = "buy_and_hold"
        elif self.strategy == 1:
            file_name += "KTNC"
            path_stra = "KTN_channel"
        file_name = file_name+"_"+str(self.optimization_setting)
        if self.weight_setting == 0:
            file_name = file_name+"_"+str(self.weight_setting)
        file_name = file_name+"_"+self.factor_name+"_"+str(self.group)+"_"+str(self.position)

        path = './portfolio_performance/'+self.factor_name+'/'+path_stra+'/'+file_name
        print('path: ', path)
        portfo_df.to_csv(path + '.csv', header=True)
        with open(path + '.txt', 'w') as file:
            file.write(json.dumps(portfo_dict))
