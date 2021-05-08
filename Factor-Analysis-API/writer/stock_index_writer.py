import math
import pandas as pd
import numpy as np
import os
import pathlib
import sys
from utils.db import ConnMysql
from utils.config import Config


COM_TYPE = ['上市', '上櫃']
STK_PRICE_TYPE = ['開盤價', '最高價', '最低價', '收盤價', '成交量', '流通在外股數']
STK_COLUMNS = ['date', 'open', 'high', 'low', 'close', 'volume']
DATE_LIST = ['20000101-20051231', '20060101-20101231',
            '20110101-20151231', '20160101-20201231']


class StockIndexWriter:

    def __init__(self):
        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_share_folder') + 'stock_index/'

        self._mydb = ConnMysql()

        stk_ind_dict = self._read_file()
        self._write_data_to_db(stk_ind_dict)

    def _read_file(self):
        stk_ind_dict = {}

        for filename in os.listdir(self._path):
            df = pd.read_excel("{}/{}".format(self._path, filename), usecols=[0, 1, 2, 3, 4, 5])
            ticker = df.columns[0].split(' ')[0]
            df = df[2:]
            df.columns = STK_COLUMNS
            df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d").astype(str)
            df = df.sort_values(by=['date'])
            stk_ind_dict[ticker] = df

        return stk_ind_dict

    def _write_data_to_db(self, ticker_dict):
        conn = self._mydb.connect_db('stock_index')

        for key, value in ticker_dict.items():
            value.to_sql(key, con=conn)
            print('successfully write '+key+' to db')
