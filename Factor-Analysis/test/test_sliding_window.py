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


window_config = {
    'factor_list': ['MOM'],
    'n_season': 1,
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

cal = Calendar('TW')
fac = Factor(window_config['factor_list'])

my_window = OneFactorWindow(window_config, report_date, cal, fac)
ticker_list = my_window.get_ticker_list()
print(ticker_list)
