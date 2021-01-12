import pandas as pd
import numpy as np
import datetime
import requests
import json


server_ip = "http://140.115.87.197:8090/"
special_factor = ['PE', 'EV_EBITDA', 'EV_S']
group_size = 150


class Factor:
    def __init__(self, factor_list):
        # 從資料庫抓出來時會按照字母大小排序= =
        factor_list.sort()
        self.factor_list = factor_list
        self.factor_df_dict = self._proc_factor_df()


    def _get_factor(self):
        print('...Factor: _get_factor()...')
        factor_list = self.factor_list

        response = requests.get(server_ip+"fac/stk_list")
        all_ticker_list = json.loads(response.text)['result']
        
        factor_df = None
        for ticker in all_ticker_list:
            payloads = {
                'ticker': ticker,
                'field': factor_list,
            }
            response = requests.get(server_ip+"fac/get_ticker_fac", params=payloads)
            fac_dict = json.loads(response.text)['result']
            column_name_list = []
            temp_factor_df = pd.DataFrame(fac_dict)
            temp_factor_df = temp_factor_df.set_index('date')
            for fac in factor_list:
                column_name_list.append(ticker+'_'+fac)
            temp_factor_df.columns = column_name_list
            if ticker == all_ticker_list[0]:
                factor_df = temp_factor_df
            else:
                factor_df = factor_df.join(temp_factor_df)
        return factor_df

    
    def _proc_factor_df(self):
        factor_df = self._get_factor()
        print('...Factor: _proc_factor_df()...')
        factor_list = self.factor_list

        factor_df_dict = {}
        for i in range(len(factor_list)):
            # 間隔抓出同一個factor
            temp_factor_df = factor_df.iloc[:, lambda df: range(i, factor_df.shape[1], len(factor_list))]
            temp_factor_df.columns = [x.split('_')[0] for x in temp_factor_df.columns]
            factor_df_dict[factor_list[i]] = temp_factor_df
        return factor_df_dict
    

    def rank_factor(self, factor, date, ascending=None):
        # print('...Factor: rank_factor()...')
        df = self.factor_df_dict[factor]
        if type(date) is not str:
            date = date.strftime('%Y-%m-%d')

        df = df.loc[date].reset_index()
        df.columns = ['ticker', factor]
        if ascending == None:
            if factor not in special_factor:
                df = df.sort_values(ascending=False, by=factor)
            else:
                df[factor] = df[factor].apply(lambda value: np.nan if value <= 0 else value)
                df = df.sort_values(ascending=True, by=factor)
        else:
            df = df.sort_values(ascending=ascending, by=factor)
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


    def check_nan(self, factor, date):
        print('...Factor: check_nan()...')
        df = self.factor_df_dict[factor]
        df = df.loc[date].reset_index()
        df.columns = ['ticker', factor]
        percent_missing = df[factor].isnull().sum() / len(df) * 100
        return round(percent_missing, 2)
