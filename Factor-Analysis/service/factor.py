import pandas as pd
import numpy as np
import datetime
import requests
import json
from multiprocessing.dummy import Pool as ThreadPool
from utils.config import Config


class Factor:

    def __init__(self, factor_list):
        # 從資料庫抓出來時會按照字母A-Z排序
        factor_list = sorted(factor_list)
        self._factor_list = factor_list
        
        self._cfg = Config()
        self._api_server_IP = self._cfg.get_value('IP', 'api_server_IP')

        # 還沒處理過的所有ticker的因子資料
        factor_df_list = self._get_all_factor_by_multithreading()
        # key 為 factor; value 為所有ticker每季度的因子資料
        self.factor_df_dict = self._proc_factor_df(factor_df_list)

    def _get_all_ticker(self):
        response = requests.get("http://{}/fac/stk_list".format(self._api_server_IP))
        all_ticker_list = json.loads(response.text)['result']
        return all_ticker_list
    
    def _get_factor(self, ticker):
        factor_list = self._factor_list
        
        payloads = {
            'ticker': ticker,
            'field': factor_list,
        }
        response = requests.get("http://{}/fac/get_ticker_fac".format(self._api_server_IP), params=payloads)
        fac_dict = json.loads(response.text)['result']
        column_name_list = []
        temp_factor_df = pd.DataFrame(fac_dict)
        temp_factor_df = temp_factor_df.set_index('date')
        for fac in factor_list:
            # 每一個 ticker 的因子資料的column以這樣的方式命名 e.g. 1101_GVI
            column_name_list.append(ticker+'_'+fac)
        temp_factor_df.columns = column_name_list
        return temp_factor_df

    def _get_all_factor_by_multithreading(self):
        # 預載所有需要用到的因子
        all_ticker_list = self._get_all_ticker()

        # 沒給參數預設會抓cup核心數 但本系統最多可能需要同時抓XX個因子故設定XX個執行緒
        pool = ThreadPool(10)
        # pool用法: (放需要平行運算的任務, 參數(需要作幾次))
        results = pool.map(self._get_factor, all_ticker_list)
        pool.close()
        pool.join()
        return results

    def _proc_factor_df(self, factor_df_list):
        # 將各個df以index(date)再以列合併
        all_factor_df = pd.concat(factor_df_list, axis=1)
        factor_list = self._factor_list
        factor_df_dict = {}

        for i in range(len(factor_list)):
            # 間隔抓出同一個factor
            temp_factor_df = all_factor_df.iloc[:, lambda df: range(i, all_factor_df.shape[1], len(factor_list))]
            temp_factor_df.columns = [x.split('_')[0] for x in temp_factor_df.columns]
            factor_df_dict[factor_list[i]] = temp_factor_df
        return factor_df_dict
    
    # 將傳入的df依照某因子排序
    # input: df             : 某個季度某個因子未排序的資料
    #        factor         : 某個因子
    #        return_list    : (bool; default=True) 是否要回傳分群過後的資料
    #        ascending      : (bool or None) 是否要小到大排序
    def rank_factor(self, df, factor, return_list=True, ascending=None):
        # 排列後空值會被排在最後
        group_size = int(self._cfg.get_value('factor', 'group_size'))
        special_factor_list = self._cfg.get_value('factor', 'special_factor_list').split(",")

        df = df.reset_index()
        df.columns = ['ticker', factor]
        # 預設None代表 如果沒有指定要怎麼排列就照因子預設排列
        if ascending == None:
            if factor not in special_factor_list:
                # 不在special_factor 就大到小排列
                df = df.sort_values(ascending=False, by=factor)
            else:
                # 在special_factor 小到大排列
                # 空值先補成-1 因為空值不能拿來跟數字比較
                df = df.fillna(-1)
                df[factor] = df[factor].apply(lambda value: np.nan if value <= 0 else value)
                df = df.sort_values(ascending=True, by=factor)
        else:
            df = df.sort_values(ascending=ascending, by=factor)
        df = df.reset_index(drop=True)
        if return_list == True:
            if df.shape[0] > group_size:
                count = (df.shape[0] // group_size) + 1
                df_list = []
                for i in range(count):
                    if i == 0: # 第一個
                        df_list.append(df.iloc[:group_size])
                    elif i+1 == count: # 最後一個
                        df_list.append(df.iloc[group_size*i:])
                    else:
                        df_list.append(df.iloc[group_size*i: group_size*(i+1)])
            else:
                df_list = [df]
            return df_list
        else:
            return df

    def check_nan(self, factor, date):
        print('[Factor]: check_nan()')
        df = self.factor_df_dict[factor]
        df = df.loc[date].reset_index()
        df.columns = ['ticker', factor]
        percent_missing = df[factor].isnull().sum() / len(df) * 100
        return round(percent_missing, 2)
