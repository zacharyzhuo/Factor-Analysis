import pandas as pd
import numpy as np
import datetime
import requests
import json


server_ip = "http://140.115.87.197:8090/"
special_factor = ['PE', 'EV_EBITDA', 'EV_S']
group_size = 150


class Factor:
    def __init__(self, factor, date):
        self.factor = factor
        self.date = date
        self.factor_df = self.get_factor()


    def get_factor(self):
        payloads = {
            'date': self.date,
            'field': [self.factor]
        }
        response = requests.get(server_ip + "fac/get_date_fac", params=payloads)
        result = json.loads(response.text)['result']
        df = pd.DataFrame(result)
        return df
    

    def rank_factor(self, ascending=None):
        df = self.factor_df
        if ascending == None:
            if self.factor not in special_factor:
                df = df.sort_values(ascending=False, by=self.factor)
            else:
                df[self.factor] = df[self.factor].apply(lambda value: np.nan if value <= 0 else value)
                df = df.sort_values(ascending=True, by=self.factor)
        else:
            df = df.sort_values(ascending=ascending, by=self.factor)
        df = df.reset_index(drop=True)
        count = (df.shape[0] // group_size) + 1
        df_list = []
        for i in range(count):
            if i == 0:
                df_list.append(df.iloc[:group_size])
            elif i+1 == count:
                df_list.append(df.iloc[group_size*i:])
            else:
                df_list.append(df.iloc[group_size*i: group_size*(i+1)])
        return df_list


    def check_nan(self):
        df = self.get_factor()
        percent_missing = df[self.factor].isnull().sum() / len(df) * 100
        return round(percent_missing, 2)
