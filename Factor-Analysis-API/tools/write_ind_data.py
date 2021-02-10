import pandas as pd
import os
import pathlib
import sys
sys.path.append("../")
from utils.db import ConnMysql


row_data_path = ['../data/raw_data/stock/', '../data/raw_data/stock_index/', '../data/raw_data/indicator/']
processed_data_path = ['../data/processed_data/stock/', '../data/processed_data/stock_index/', '../data/processed_data/indicator/']

ind_name_list = ['date', '歸屬母公司淨利（損）', '股東權益總額', '每股淨值(B)',
            '收盤價(元)', '每股盈餘', '報酬率(季)', '本益比-TSE',
            '季底普通股市值', '淨負債', '稅前息前折舊前淨利', '營業收入淨額',
            '自由現金流量(D)', '負債及股東權益總額', '特別股負債－非流動', '應付公司債－非流動',  
            '銀行借款－非流動', '其他長期借款－非流動', 'FV變動入損益非流動金融負債－指定公平價值－公司債'
            ]

mydb = ConnMysql()
db_name = ['stock', 'stock_index', 'indicator']


def proc_ind_data():
    ind_dict = {}
    for filename in os.listdir(row_data_path[2]):
        filepath = str(pathlib.Path().absolute())+'/'+row_data_path[2]+filename
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
        print(ticker)
        print(ticker_df)
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
ind_dict = proc_ind_data()
ticker_data_dict = trans_ind_to_one_symbol(ind_dict)
write_data_to_mysql(db_name[2], ticker_data_dict)
