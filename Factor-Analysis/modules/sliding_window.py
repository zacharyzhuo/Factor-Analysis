import pandas as pd
import numpy as np
import datetime
import requests
import json

from window.one_factor_window import OneFactorWindow
from window.two_factor_window import TwoFactorWindow


class SlidingWindow:

    def __init__(self, window_config, cal, fac):
        self.window_config = window_config
        self.cal = cal
        self.fac = fac
        self.report_date_list = cal.get_report_date_list(window_config['start_date'], window_config['end_date'])
        self._slide_window()

    def _slide_window(self):
        print('[SlidingWindow]: _slide_window()')
        window_config = self.window_config

        for report_date in self.report_date_list:
            # one factor
            if len(window_config['factor_list']) == 1:
                my_window = OneFactorWindow(window_config, report_date, self.cal, self.fac)

            # two factor
            elif len(window_config['factor_list']) == 2:
                my_window = TwoFactorWindow(window_config, report_date, self.cal, self.fac)

            if window_config['if_first'] == True:
                my_window.get_ticker_list()
                
            self.window_config = my_window.play_window()
        
        # print('window_config: ', self.window_config)
