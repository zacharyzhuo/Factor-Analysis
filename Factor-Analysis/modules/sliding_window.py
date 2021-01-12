import pandas as pd
import numpy as np
import datetime
import requests
import json

from strategys.buy_and_hold_window import BuyAndHoldWindow


# portfolio_config = {
#     'ticker_list': ['1101'],
#     'factor_list': ['MOM'],
#     'n_season': 1,
#     'group': 1,
#     'position': 5,
#     'start_date': '2000-01-01',
#     'end_date': '2017-12-31',
# }

class SlidingWindow:
    def __init__(self, portfolio_config, cal, fac):
        self.portfolio_config = portfolio_config
        self.cal = cal
        self.fac = fac
        self.report_date_list = cal.get_report_date_list(portfolio_config['start_date'], portfolio_config['end_date'])
        self.window_data_dict = {}
        self._slide_window()

    def _slide_window(self):
        print('...SlidingWindow: _slide_window()...')
        for report_date in self.report_date_list:
            my_window = BuyAndHoldWindow(self.portfolio_config, report_date, self.cal, self.fac)
            break

