import math
import pandas as pd
import numpy as np
from utils.db import ConnMysql
from utils.config import Config


COM_TYPE = ['上市', '上櫃']
STK_PRICE_TYPE = ['開盤價', '最高價', '最低價', '收盤價', '成交量', '流通在外股數']
STK_COLUMNS = ['date', 'open', 'high', 'low', 'close', 'volume', 'outstanding_share']
DATE_LIST = ['20000101-20051231', '20060101-20101231',
            '20110101-20151231', '20160101-20201231']


class StockWriter:

    def __init__(self):
        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_share_folder') + 'stock/'

        self._mydb = ConnMysql()

        stk_dict = self._read_file()
        ticker_dict = self._trans_to_one_symbol(stk_dict)
        self._write_data_to_db(ticker_dict)

    def _read_file(self):
        stk_dict = {}

        for i in range(len(COM_TYPE)):
            temp_dict = {}

            for j in range(len(STK_PRICE_TYPE)):
                df = pd.read_excel("{}{}_{}_{}.xlsx".format(
                    self._path, COM_TYPE[i], STK_PRICE_TYPE[j], DATE_LIST[0]))
                df = df.iloc[1:]

                for k in range(1, len(DATE_LIST)):
                    temp_df = pd.read_excel("{}{}_{}_{}.xlsx".format(
                        self._path, COM_TYPE[i], STK_PRICE_TYPE[j], DATE_LIST[k]))
                    temp_df = temp_df.iloc[1:]
                    df = df.append(temp_df)

                df.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
                df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d").astype(str)
                df = df.sort_values(by=['date'])
                temp_dict[STK_PRICE_TYPE[j]] = df
                print(df.shape)
                print("read {}_{}".format(COM_TYPE[i], STK_PRICE_TYPE[j]))

            stk_dict[COM_TYPE[i]] = temp_dict

        return stk_dict

    def _adjust_stk_price(self, value):
        if value < 10:
            value = math.ceil(value * 100) / 100.0

        elif value > 10 and value < 50:
            value = math.ceil(value * 100) / 100.0
            value_list = str(value).split('.')

            if len(value_list[1]) == 1:
                value_list[1] = value_list[1][0] + '0'

            if (int(value_list[0][1]) == 9 and int(value_list[1][0]) == 9
                and int(value_list[1][1]) > 5) or (int(value_list[1][0]) == 9
                and int(value_list[1][1]) > 5):
                value_list[0] = str(int(value_list[0]) + 1)
                value_list[1] = '00'

            else:
                if int(value_list[1][1]) < 5 and int(value_list[1][1]) != 0:
                    value_list[1] = value_list[1][0] + '5'

                elif int(value_list[1][1]) > 5:
                    value_list[1] = str(int(value_list[1][0]) + 1) + '0'

            value_list = ".".join(value_list)
            value = float(value_list)

        elif value > 50 and value < 100:
            value = math.ceil(value * 10) / 10.0

        elif value > 100 and value < 500:
            value = math.ceil(value * 10) / 10.0
            value_list = str(value).split('.')

            if int(value_list[1][0]) < 5 and int(value_list[1][0]) != 0:
                value_list[1] = '5'

            elif int(value_list[1][0]) > 5:
                value_list[0] = str(int(value_list[0]) + 1)
                value_list[1] = '00'

            value_list = ".".join(value_list)
            value = float(value_list)

        elif value > 500 and value < 1000:
            value = math.ceil(value * 1) / 1.0

        elif value > 1000:
            value = math.ceil(value)
            value_list = str(value)

            if int(value_list[3]) < 5 and int(value_list[3]) != 0:
                value_list = value_list[:-1] + '5'

            elif int(value_list[3]) > 5:
                num = value_list[:3]
                num = str(int(num) + 1)
                value_list = num + '0'

            value_list = "".join(value_list)
            value = float(value_list)

        return value

    def _trans_to_one_symbol(self, stk_dict):
        ticker_dict = {}

        for i in range(len(COM_TYPE)):
            stock_price_type_arr = []
            ticker_df = pd.DataFrame()

            for j in range(len(STK_PRICE_TYPE)):
                df = stk_dict[COM_TYPE[i]][STK_PRICE_TYPE[j]]
                columns_name = df.columns
                length = len(columns_name)
                stock_price_type_arr.append(df)

            for k in range(1, length):
                ticker = columns_name[k].split()[0]
                ticker_df = pd.DataFrame(
                    stock_price_type_arr[0][['date']], columns=['date']
                )
                ticker_df['open'] = stock_price_type_arr[0][[columns_name[k]]]
                ticker_df['high'] = stock_price_type_arr[1][[columns_name[k]]]
                ticker_df['low'] = stock_price_type_arr[2][[columns_name[k]]]
                ticker_df['close'] = stock_price_type_arr[3][[columns_name[k]]]
                ticker_df['volume'] = stock_price_type_arr[4][[columns_name[k]]]
                ticker_df['outstanding_share'] = stock_price_type_arr[5][[columns_name[k]]]

                ticker_df.columns = STK_COLUMNS
                ticker_df['open'] = ticker_df['open'].apply(lambda x: self._adjust_stk_price(x))
                ticker_df['high'] = ticker_df['high'].apply(lambda x: self._adjust_stk_price(x))
                ticker_df['low'] = ticker_df['low'].apply(lambda x: self._adjust_stk_price(x))
                ticker_df['close'] = ticker_df['close'].apply(lambda x: self._adjust_stk_price(x))
                ticker_dict[ticker] = ticker_df

        print('successfully transfer to one symbol')
        return ticker_dict

    def _write_data_to_db(self, ticker_dict):
        conn = self._mydb.connect_db('stock')

        for key, value in ticker_dict.items():
            value.to_sql(key, con=conn)
            print('successfully write '+key+' to db')
