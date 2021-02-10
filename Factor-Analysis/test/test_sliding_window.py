import pandas as pd
import numpy as np
import math
import datetime
import requests
import json
import talib
import os
import sys
sys.path.append("../")

from service.factor import Factor
from service.calendar import Calendar
from modules.sliding_window import SlidingWindow
from window.one_factor_window import OneFactorWindow
from window.two_factor_window import TwoFactorWindow


window_config = {
    'strategy': 1,
    'factor_list': ['PE', 'FC_P'],
    'n_season': 0,
    'group': 1,
    'position': 5,
    'start_date': '2010-01-01',
    'end_date': '2017-12-31',
    'if_first': True,
    'ticker_list': [],
    'signal': {},
    'weight': {},
}

report_date = '2010-03-31'
factor_list = window_config['factor_list']
# cal = Calendar('TW')
# fac = Factor(factor_list)


# my_window = SlidingWindow(window_config, cal, fac)

# my_window = TwoFactorWindow(window_config, report_date, cal, fac)
# ticker_list = my_window.get_ticker_list()
# print(ticker_list)

x = range(5, 50, 5)
y = np.arange(0.1, 2.0, 0.1)
print(x)
print(type(x))
print(y)
print(type(y))