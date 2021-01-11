import pandas as pd
import numpy as np
import datetime
import requests
import json

from modules.calendar import Calendar
from modules.factor import Factor
from modules.portfolio import Portfolio


class MyStrategy:
    def __init__(self, strategy, optimization_setting, weight_setting, factor_name,
                group, position, start_equity, start_date, end_date):
        print('----------------------')
        print('strategy: ', strategy)
        print('optimization_setting: ', optimization_setting)
        print('weight_setting: ', weight_setting)
        print('factor_name: ', factor_name)
        print('group: ', group)
        print('position: ', position)
        print('----------------------')

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
        print('...MyStrategy: get_ticker_list...')
        date = self.cal.advance_date(self.start_date, 1, 's')
        print('backtesting period: ' + self.start_date + ' to ' + self.end_date)
        print('get factor data at ' + date)
        self.factor = Factor(self.factor_name, date)
        # print(self.factor.factor_df)
        ranking_list = self.factor.rank_factor()
        print('get group ' + str(self.group) + ' from ranking list')
        ticker_group_df = ranking_list[self.group - 1]
        # print(ticker_group_df)
        print('get a ticker list of top ' + str(self.position) + ' from group ' + str(self.group))
        ticker_list = ticker_group_df['ticker'].iloc[0: self.position].tolist()
        print('ticker_list: ', ticker_list)
        return ticker_list
    

    def create_portfolio(self):
        ticker_list = self.get_ticker_list()
        print('...MyStrategy: create_portfolio...')
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
        print('...MyStrategy: write_portfolio_performance...')
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
        portfo_df.to_csv(path + '.csv', header=True)
        with open(path + '.json', 'w') as file:
            json.dump(portfo_dict, file)
