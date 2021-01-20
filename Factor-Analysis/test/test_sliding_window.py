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

from modules.factor import Factor
from modules.calendar import Calendar
from modules.sliding_window import SlidingWindow
from strategys.one_factor_window import OneFactorWindow
from strategys.two_factor_window import TwoFactorWindow
from strategys.bbands_window import BBandsWindow


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
cal = Calendar('TW')
fac = Factor(factor_list)


# my_window = SlidingWindow(window_config, cal, fac)

my_window = BBandsWindow(window_config, report_date, cal, fac)
ticker_list = my_window.get_ticker_list()
print(ticker_list)
