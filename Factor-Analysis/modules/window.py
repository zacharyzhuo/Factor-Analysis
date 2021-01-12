import pandas as pd
import numpy as np
import datetime
import requests
import json


class Window:
    def __init__(self, portfolio_config):
        self.portfolio_config = portfolio_config
    
    def set_t1(self):

        ti_para = {
            date = '2010-03-31',
            ticker_list = ['3090', '4205', '1521', '4909', '2028'],
            signal = {
                '3090': 0,
                '4205': 1,
                '1521': 2,
                '4909': 0, 
                '2028': 1,
            }
        }

        t1_data = {
            start_date = '2009-12-31',
            end_date = '2010-03-31',
            ticker_list = ['3090', '4205', '1521', '4909', '2028']
            factor_list = ['GVI', 'MOM']
            factor_value_list = [],
        }

    def set_t2(self):
