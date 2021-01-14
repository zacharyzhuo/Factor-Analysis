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


window_config = {
    'factor_list': ['MOM'],
    'n_season': 1,
    'group': 1,
    'position': 5,
    'start_date': '2010-01-01',
    'end_date': '2017-12-31',
    'if_first': True,
    'ticker_list': [],
    'signal': {}
}

cal = Calendar('TW')
fac = Factor(window_config['factor_list'])

date = cal.advance_date(window_config['start_date'], 1, 's')
group_list = fac.rank_factor(window_config['factor_list'][0], date)
rank_list = group_list[window_config['group'] - 1]
ticker_list = rank_list['ticker'].iloc[0: window_config['position']].tolist()
window_config['ticker_list'] = ticker_list

sliding_window = SlidingWindow(window_config, cal, fac)
# sliding_window = SlidingWindow(window_config, cal)
# x = cal.get_report_date('2010-11-12', -1)
# print(x)
