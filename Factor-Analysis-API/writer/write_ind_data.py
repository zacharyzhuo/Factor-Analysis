import pandas as pd
import os
import pathlib
import sys
sys.path.append("../")
from utils.db import ConnMysql
from utils.config import Config


row_data_path = ['../data/raw_data/stock/', '../data/raw_data/stock_index/', '../data/raw_data/indicator/']
processed_data_path = ['../data/processed_data/stock/', '../data/processed_data/stock_index/', '../data/processed_data/indicator/']

file_name_list = [
    '常續性稅後淨利', '股東權益總額', '每股淨值(B)',
    '每股盈餘', '季底普通股市值', '淨負債', '稅前息前折舊前淨利', '營業收入淨額',
    '自由現金流量(D)', '負債及股東權益總額', '特別股負債－非流動', '應付公司債－非流動',  
    '銀行借款－非流動', '其他長期借款－非流動', '營業成本', '期末普通股－現金股利',
    '期末特別股－現金股利', '來自營運之現金流量', 'FV變動入損益非流動金融負債－指定公平價值－公司債',
    '收盤價(元)', '流通在外股數(千股)', '本益比-TSE'
]

ind_name_list = [
    'date', '常續性稅後淨利', '股東權益總額', '每股淨值(B)',
    '每股盈餘', '季底普通股市值', '淨負債', '稅前息前折舊前淨利', '營業收入淨額',
    '自由現金流量(D)', '負債及股東權益總額', '特別股負債－非流動', '應付公司債－非流動',  
    '銀行借款－非流動', '其他長期借款－非流動', '營業成本', '期末普通股－現金股利',
    '期末特別股－現金股利', '來自營運之現金流量', 'FV變動入損益非流動金融負債－指定公平價值－公司債',
    '收盤價(元)', '流通在外股數(千股)', '本益比-TSE'
]

mydb = ConnMysql()
db_name = ['stock', 'stock_index', 'indicator']

config = Config()
path = config.get_value('path', 'path_to_share_folder')
path = path + 'indicator/'


def proc_ind_data():
    ind_dict = {}
    for filename in file_name_list:
        filepath = "{}{}.xlsx".format(path, filename)
        df = pd.read_excel(filepath)
        ind_name = df.iloc[0][1]
        df = df.drop(0, axis=0)
        df.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
        df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d").astype(str)
        df = df.sort_values(by=['date'])
        df = df.reset_index(drop=True)
        ind_dict[ind_name] = df
        print(ind_name)
        print(df.shape)
    print('successfully processed indicator data')
    return ind_dict

def trans_ind_to_one_symbol(ind_dict):
    ticker_data_dict = {}
    ticker_list = ind_dict[ind_name_list[1]].columns.tolist()
    ticker_list.pop(0)
    for elm in ticker_list:
        ind_list = []
        ticker = elm.split()[0]
        date_column_data = ind_dict[ind_name_list[1]][['date']]
        ind_list.append(date_column_data)
        for ind in ind_name_list:
            if ind == ind_name_list[0]:
                pass
            else:
                ind_list.append(ind_dict[ind][[elm]])
        ticker_df = pd.concat(ind_list, axis=1)
        ticker_df.columns = ind_name_list
        ticker_data_dict[ticker] = ticker_df
    print('successfully transfer to one symbol')
    return ticker_data_dict

def write_data_to_mysql(db_name, ticker_data_dict):
    conn = mydb.connect_db(db_name)
    for key, value in ticker_data_dict.items():
        value.to_sql(key, con=conn)
        print('successfully write '+key+' to db')

def check_if_add_ticker(ind_dict):
    new_columns_list = ind_dict[ind_name_list[6]].columns.tolist()
    old_columns_list = ind_dict[ind_name_list[1]].columns.tolist()
    
    print("add the following ticker:")
    for elm in new_columns_list:
        if elm not in old_columns_list:
            print(elm)
            
    print("del the following ticker:")
    for elm in old_columns_list:
        if elm not in new_columns_list:
            print(elm)
    # print(old_columns_list)
    # print(after_new_columns_list)

"""
write indicator data
"""
# ind_dict = proc_ind_data()
# ticker_data_dict = trans_ind_to_one_symbol(ind_dict)
# write_data_to_mysql(db_name[2], ticker_data_dict)
