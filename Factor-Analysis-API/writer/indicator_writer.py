import math
import pandas as pd
import numpy as np
from multiprocessing.dummy import Pool as ThreadPool
# 寫入DF到資料庫用這個套件比較好用
from utils.db import ConnMysql
from utils.config import Config


IND_LIST = [
    # '常續性稅後淨利', '股東權益總額', '每股淨值(B)', '每股盈餘',
    # '季底普通股市值', '淨負債', '稅前息前折舊前淨利', '營業收入淨額',
    # '自由現金流量(D)', '負債及股東權益總額', '特別股負債－非流動', '應付公司債－非流動',  
    # '銀行借款－非流動', '其他長期借款－非流動', '營業成本', '期末普通股－現金股利',
    # '期末特別股－現金股利', '來自營運之現金流量', 'FV變動入損益非流動金融負債－指定公平價值－公司債', '收盤價(元)',
    # '流通在外股數(千股)', '本益比-TSE', 'MOM(7個月相對強弱)', 'MOM(52週價格範圍)'

    '每股盈餘', '季底普通股市值', '淨負債', '稅前息前折舊前淨利',
    '營業收入淨額', '自由現金流量(D)', '負債及股東權益總額', '常續性稅後淨利', 
    '股東權益總額', '每股淨值(B)', '來自營運之現金流量', '收盤價(元)', 
    '本益比-TSE', 'MOM(季)'
]


class IndicatorWriter:

    def __init__(self):
        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_share_folder') + 'indicator/'

        self._mydb = ConnMysql()

        self._ticker_list = []

        ind_dict = self._read_file_by_multithreading()
        ticker_data_dict = self._trans_to_one_symbol(ind_dict)
        self._write_data_to_db(ticker_data_dict)

    def _read_file(self, ind):
        filepath = "{}{}.xlsx".format(self._path, ind)
        df = pd.read_excel(filepath)

        # 第一個 row 都是這個指標的名字 (date, ind1, ind2 ...)
        ind_name = df.iloc[0][1]
        df = df.drop(0, axis=0)
        df.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
        df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d").astype(str)
        df = df.sort_values(by=['date']).reset_index(drop=True)
        # df = df.where(pd.notnull(df), None)
        df.columns = [x.split(" ")[0] for x in df.columns.tolist()]
        print("{}: shape{}".format(ind_name, df.shape))
        return {ind_name: df}
    
    def _read_file_by_multithreading(self):
        ind_dic = {}

        # 沒給參數預設會抓cup核心數
        pool = ThreadPool(22)
        # pool用法: (放需要平行運算的任務, 參數(需要作幾次))
        results = pool.map(self._read_file, IND_LIST)
        pool.close()
        pool.join()

        for result in results:
            if result:
                ind_dic[list(result.keys())[0]] = list(result.values())[0]
        return ind_dic

    def _trans_to_one_symbol(self, ind_dict):
        ticker_data_dict = {}
        # 因為每個檔案格式都長一樣 故以第一個檔案的 columns name 為準
        ticker_list = ind_dict[IND_LIST[0]].columns.tolist()
        # 去掉 date
        ticker_list.pop(0)
        self._ticker_list = ticker_list
        columns_name_list = IND_LIST.copy()
        columns_name_list.insert(0, 'date')
        
        for ticker in self._ticker_list:
            ticker_ind_list = []
            # 同理 以第一個檔案的 date columns 為準
            ticker_ind_list.append(ind_dict[IND_LIST[0]][['date']])

            for ind in IND_LIST:
                ticker_ind_list.append(ind_dict[ind][[ticker]])

            ticker_df = pd.concat(ticker_ind_list, axis=1)
            ticker_df.columns = columns_name_list
            ticker_data_dict[ticker] = ticker_df
        return ticker_data_dict

    def _write_data_to_db(self, ticker_dict):
        conn = self._mydb.connect_db('indicator')

        for key, value in ticker_dict.items():
            value.to_sql(key, con=conn)
            print('successfully write '+key+' to db')
