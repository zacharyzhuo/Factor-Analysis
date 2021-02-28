import pandas as pd
import os
import pathlib
import sys
import math
sys.path.append("../")
from utils.db import ConnMysql
from utils.config import Config


company_type = ['上市', '上櫃']
stock_price_type = ['開盤價', '最高價', '最低價', '收盤價', '成交量', '流通在外股數']
stock_columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'outstanding_share']
date_list = ['20000101-20051231', '20060101-20101231',
            '20110101-20151231', '20160101-20201231']

mydb = ConnMysql()
db_name = ['stock', 'stock_index', 'indicator']

config = Config()
path = config.get_value('path', 'path_to_share_folder')
path = path + 'stock/'


def proc_stk_data():
    for i in range(len(company_type)):
        for j in range(len(stock_price_type)):
            df = pd.read_excel("{}raw_data/{}_{}_{}.xlsx".format(
                path, company_type[i], stock_price_type[j], date_list[0]))
            df = df.iloc[1:]
            for k in range(1, len(date_list)):
                temp_df = pd.read_excel("{}raw_data/{}_{}_{}.xlsx".format(
                    path, company_type[i], stock_price_type[j], date_list[k]))
                temp_df = temp_df.iloc[1:]
                df = df.append(temp_df)
            df.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
            df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d").astype(str)
            df = df.sort_values(by=['date'])
            df = df.set_index('date')
            df.to_csv("{}processed_data/{}_{}_20000101-20201231.csv".format(
                path, company_type[i], stock_price_type[j]),
                header=True, encoding="utf_8_sig")
            print("successfully write to csv")

def trans_stk_price(value):
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

def trans_stk_to_one_symbol():
    ticker_dict = {}
    for i in range(len(company_type)):
        stock_price_type_arr = []
        for j in range(len(stock_price_type)):
            df = pd.read_csv("{}processed_data/{}_{}_20000101-20201231.csv".format(path, company_type[i], stock_price_type[j]))
            columns_name = df.columns
            length = len(columns_name)
            stock_price_type_arr.append(df)
        for k in range(1, length):
            ticker = columns_name[k].split()[0]
            date_df = stock_price_type_arr[0][['date']]
            open_df = stock_price_type_arr[0][[columns_name[k]]]
            high_df = stock_price_type_arr[1][[columns_name[k]]]
            low_df = stock_price_type_arr[2][[columns_name[k]]]
            close_df = stock_price_type_arr[3][[columns_name[k]]]
            volume_df = stock_price_type_arr[4][[columns_name[k]]]
            outstanding_share_df = stock_price_type_arr[5][[columns_name[k]]]

            df_list = [date_df, open_df, high_df, low_df, close_df, volume_df, outstanding_share_df]
            ticker_df = pd.concat(df_list, axis=1)
            ticker_df.columns = stock_columns
            ticker_df['open'] = ticker_df['open'].apply(lambda x: trans_stk_price(x))
            ticker_df['high'] = ticker_df['high'].apply(lambda x: trans_stk_price(x))
            ticker_df['low'] = ticker_df['low'].apply(lambda x: trans_stk_price(x))
            ticker_df['close'] = ticker_df['close'].apply(lambda x: trans_stk_price(x))
            ticker_dict[ticker] = ticker_df
    print('successfully transfer to one symbol')
    return ticker_dict

def write_data_to_mysql(db_name, ticker_dict):
    conn = mydb.connect_db(db_name)
    for key, value in ticker_dict.items():
        value.to_sql(key, con=conn)
        print('successfully write '+key+' to db')


"""
write stock data
"""
# proc_stk_data()

# ticker_dict = trans_stk_to_one_symbol()
# write_data_to_mysql(db_name[0], ticker_dict)
