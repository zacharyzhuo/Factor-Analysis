import pandas as pd
import numpy as np
import datetime
import sys
sys.path.append("../")
from utils.db import ConnMysql


ind_name_list = ['date', '歸屬母公司淨利（損）', '股東權益總額', '每股淨值(B)',
            '收盤價(元)', '每股盈餘', '報酬率(季)', '本益比-TSE',
            '季底普通股市值', '淨負債', '稅前息前折舊前淨利', '營業收入淨額',
            '自由現金流量(D)', '負債及股東權益總額', '特別股負債－非流動', '應付公司債－非流動',  
            '銀行借款－非流動', '其他長期借款－非流動', 'FV變動入損益非流動金融負債－指定公平價值－公司債'
            ]

mydb = ConnMysql()
db_name = ['stock', 'stock_index', 'indicator', 'factor']


def read_one_ticker(ticker):
    print('read ', ticker)
    conn = mydb.connect_db(db_name[2])
    output = []
    sql = 'SELECT * FROM `' + ticker + '`'
    inds = conn.execute(sql)
    if inds:
        for ind in inds:
            ind_dict = dict(ind)
            del ind_dict['index']
            output.append(ind_dict)
    df = pd.DataFrame(output)
    df.iloc[:, 1:] = df.iloc[:, 1:].astype(float)
    return df

def cal_factor_data():
    factor_dict = {}
    conn = mydb.connect_db(db_name[2])
    ticker_list = conn.table_names()
    for elm in ticker_list:
        print('calculate '+elm+' factor')
        factor_df = pd.DataFrame()
        df = read_one_ticker(elm)
        factor_df['date'] = df[ind_name_list[0]]
        # GVI: (每股淨值(B) / 收盤價) x (1+(歸屬母公司淨利（損） / 股東權益總額)) ^ 20
        factor_df['GVI'] = df[ind_name_list[3]] / df[ind_name_list[4]] * (1 + (df[ind_name_list[1]] / df[ind_name_list[2]])) ** 20
        # EPS: 每股盈餘
        factor_df['EPS'] = df[ind_name_list[5]]
        # MOM: 報酬率(季)
        factor_df['MOM'] = df[ind_name_list[6]]
        # PE: 本益比-TSE
        factor_df['PE'] = df[ind_name_list[7]]
        # EV_EBITDA: (季底普通股市值 + 淨負債) / 稅前息前折舊前淨利
        factor_df['EV_EBITDA'] = (df[ind_name_list[8]] + df[ind_name_list[9]]) / df[ind_name_list[10]]
        # EV_S: (季底普通股市值 + 淨負債) / 營業收入淨額
        factor_df['EV_S'] = (df[ind_name_list[8]] + df[ind_name_list[9]]) / df[ind_name_list[11]]
        # FC_P: 自由現金流量 / 季底普通股市值
        factor_df['FC_P'] = df[ind_name_list[12]] / df[ind_name_list[8]]
        # CROIC: 自由現金流量 / 負債及股東權益總額
        factor_df['CROIC'] = df[ind_name_list[12]] / df[ind_name_list[13]]
        # FC_OI: 自由現金流量 / 營業收入淨額
        factor_df['FC_OI'] = df[ind_name_list[12]] / df[ind_name_list[11]]
        # FC_LTD: 自由現金流量 / (特別股負債－非流動 + 應付公司債－非流動 + 銀行借款－非流動 + 其他長期借款－非流動 + FV變動入損益非流動金融負債－指定公平價值－公司債
        df[ind_name_list[14]] = df[ind_name_list[14]].fillna(0)
        df[ind_name_list[15]] = df[ind_name_list[15]].fillna(0)
        df[ind_name_list[16]] = df[ind_name_list[16]].fillna(0)
        df[ind_name_list[17]] = df[ind_name_list[17]].fillna(0)
        df[ind_name_list[18]] = df[ind_name_list[18]].fillna(0)
        LTD_df = df[ind_name_list[14]] + df[ind_name_list[15]] + df[ind_name_list[16]] + df[ind_name_list[17]] + df[ind_name_list[18]]
        LTD_df = LTD_df.astype(np.float)
        df[ind_name_list[12]] = df[ind_name_list[12]].astype(np.float)
        factor_df['FC_LTD'] = df[ind_name_list[12]].divide(LTD_df) 
        factor_df['FC_LTD'] = factor_df['FC_LTD'].replace(np.inf, 0)
        
        # 除數為0導致出現inf
        factor_df = factor_df.replace([np.inf, -np.inf], np.nan)
        factor_dict[elm] = factor_df
    return factor_dict

def write_data_to_mysql(db_name, ticker_dict):
    conn = mydb.connect_db(db_name)
    for key, value in ticker_dict.items():
        value.to_sql(key, con=conn)
        print('successfully write '+key+' to db')


"""
calculate and write indicator data
"""
factor_dict = cal_factor_data()
write_data_to_mysql(db_name[3], factor_dict)
