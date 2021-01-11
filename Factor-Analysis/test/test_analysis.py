import pandas as pd
import numpy as np
import datetime
import requests
import json
import talib
import sys
sys.path.append("../")

from backtesting import Backtest, Strategy
from strategys.ktn_channel import KTNChannel
from strategys.buy_and_hold import BuyAndHold

from modules.calendar import Calendar
from modules.factor import Factor
from modules.portfolio import Portfolio
from modules.analysis import Analysis


server_ip = "http://140.115.87.197:8090/"

strategy = [0, 1]                           # 0: BuyAndHold; 1: KTNChannel
optimization_setting = [0, 1]               # 0: 無變數(or單一變數); 1: 最佳化變數
weight_setting = [0, 1, 2]                  # 0: equal_weight; 1: equal_risk(ATR); 2: equal_risk(SD)
factor_name = ['GVI', 'EPS', 'MOM', 'PE', 'EV_EBITDA', 'EV_S', 'FC_P', 'CROIC', 'FC_OI', 'FC_LTD']
group = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
position = [5, 10, 15, 30, 90, 150]

start_equity = 10000000
start_date = '2010-01-01'
end_date = '2017-12-31'
risk_free_rate = 0.01

cal = Calendar('TW')
date_list = cal.get_report_date_list('2010-01-01', '2017-12-31')
print(date_list)
date = cal.get_report_date('2010-01-30')
print(date)

# date = '2011-03-31'
# how = 1
# date = cal.advance_date(date, how, 's')
# print(date)

# analysis = Analysis(start_equity, start_date, end_date, risk_free_rate)