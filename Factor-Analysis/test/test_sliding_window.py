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


portfolio_config = {
    'ticker_list': ['1101'],
    'factor_list': ['MOM'],
    'n_season': 1,
    'group': 1,
    'position': 5,
    'start_date': '2010-01-01',
    'end_date': '2017-12-31',
}

cal = Calendar('TW')
fac = Factor(portfolio_config['factor_list'])
sliding_window = SlidingWindow(portfolio_config, cal, fac)
# sliding_window = SlidingWindow(portfolio_config, cal)
# x = cal.get_report_date('2010-11-12', -1)
# print(x)
