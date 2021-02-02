import pandas as pd
import numpy as np
import datetime
import requests
import json
import talib
import sys
sys.path.append("../")

from backtesting import Backtest, Strategy
from strategy.ktn_channel import KTNChannel
from strategy.buy_and_hold import BuyAndHold

from api.calendar import Calendar
from api.factor import Factor
from modules.portfolio import Portfolio
from analysis.analysis import Analysis


server_ip = "http://140.115.87.197:8090/"

factor_list = ['GVI', 'EPS', 'MOM', 'PE', 'EV_EBITDA', 'EV_S', 'FC_P', 'CROIC', 'FC_OI', 'FC_LTD']
# 0: equal_weight; 1: equal_risk(ATR); 2: equal_risk(SD)
weight_setting = [0, 1, 2]                  
n_season = [0, 1]
group = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
position = [5, 10, 15, 30, 90, 150]

start_equity = 10000000
start_date = '2010-01-01'
end_date = '2017-12-31'

analysis = Analysis(start_equity, start_date, end_date)
analysis.analysis_factor_performance(factor_list[1])
# analysis.anslysis_portfolio()
# analysis.rank_portfolio_return()
# analysis.plot_net_profit_years()