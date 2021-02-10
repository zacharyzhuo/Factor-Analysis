import pandas as pd
import os
import pathlib
import sys
sys.path.append("../")
from utils.db import ConnMysql


row_data_path = ['../data/raw_data/stock/', '../data/raw_data/stock_index/', '../data/raw_data/indicator/']
processed_data_path = ['../data/processed_data/stock/', '../data/processed_data/stock_index/', '../data/processed_data/indicator/']
stock_columns = ['date', 'open', 'high', 'low', 'close', 'volume']

mydb = ConnMysql()
db_name = ['stock', 'stock_index', 'indicator']


def proc_stk_idx_data():
    for filename in os.listdir(row_data_path[1]):
        filepath = str(pathlib.Path().absolute())+'/'+row_data_path[1]+filename
        df = pd.read_excel(filepath, usecols=[0, 1, 2, 3, 4, 5])
        ticker = df.columns[0].split(' ')[0]
        df = df[2:]
        df.columns = stock_columns
        df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d").astype(str)
        df = df.sort_values(by=['date'])
        df = df.set_index('date')
        print(df)
        df.to_csv(processed_data_path[1]+ticker+'.csv', header=True, encoding="utf_8_sig")

def read_stk_idx_data():
    ticker_dict = {}
    for filename in os.listdir(processed_data_path[1]):
        filepath = str(pathlib.Path().absolute())+'/'+processed_data_path[1]+filename
        df = pd.read_csv(filepath)
        ticker_name = filename.split('.')[0]
        ticker_dict[ticker_name] = df
    return ticker_dict

def write_data_to_mysql(db_name, ticker_dict):
    conn = mydb.connect_db(db_name)
    for key, value in ticker_dict.items():
        value.to_sql(key, con=conn)
        print('successfully write '+key+' to db')


"""
write stock index data
"""
# proc_stk_idx_data()
ticker_dict = read_stk_idx_data()
write_data_to_mysql(db_name[1], ticker_dict)
