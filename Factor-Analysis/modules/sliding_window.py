import pandas as pd
import numpy as np
import datetime
import requests
import json

from modules.calendar import Calendar
from modules.factor import Factor
from modules.window import Window


portfolio_config = {
    factor_list = ['GVI', 'MOM'],
    n_season = 1,
    group = 1,
    position = 5,
    start_date = '2000-01-01',
    end_date = '2017-12-31',
}

class SlidingWindow:
    def __init__(self, portfolio_config):
        self.portfolio_config = portfolio_config

        self.get_ticker_list()
        self.window = Window(self.portfolio_config)
    
    def get_ticker_list(self):
        cal = Calendar("TW")
        date = cal.advance_date(self.portfolio_config.start_date, self.portfolio_config.n_season, 's')
        # 選股濾網可寫在Factor裡面
        ticker_list = Factor('GVI', date).rank_factor
        self.portfolio_config['ticker_list'] = ticker_list
    
    def set_t1_data(self):

    def set_t2_data(self):
