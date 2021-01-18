import pandas as pd
import numpy as np
import datetime
import requests
import json

from strategys.one_factor_window import OneFactorWindow


class SlidingWindow:
    def __init__(self, window_config, cal, fac):
        self.window_config = window_config
        self.cal = cal
        self.fac = fac
        self.report_date_list = cal.get_report_date_list(window_config['start_date'], window_config['end_date'])
        self._slide_window()

    def _slide_window(self):
        print('...SlidingWindow: _slide_window()...')
        for report_date in self.report_date_list:
            my_window = OneFactorWindow(self.window_config, report_date, self.cal, self.fac)
            self.window_config = my_window.play_window()
        # print('window_config: ', self.window_config)
