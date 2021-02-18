import pandas as pd
import numpy as np
import datetime
import sys
sys.path.append("../")
from utils.db import ConnMysql


# 0 1 2 3
# 4 5 6 7
# 8 9 10 11
# 12 13 14 15
# 16 17 18 19
# 20 21 22
i_list = [
    'date', '常續性稅後淨利', '股東權益總額', '每股淨值(B)',
    '每股盈餘', '季底普通股市值', '淨負債', '稅前息前折舊前淨利',
    '營業收入淨額', '自由現金流量(D)', '負債及股東權益總額', '特別股負債－非流動',
    '應付公司債－非流動', '銀行借款－非流動', '其他長期借款－非流動', '營業成本',
    '期末普通股－現金股利', '期末特別股－現金股利', '來自營運之現金流量', 'FV變動入損益非流動金融負債－指定公平價值－公司債',
    '收盤價(元)', '流通在外股數(千股)', '本益比-TSE'
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
        factor_df['date'] = df[i_list[0]]
        # GVI: (每股淨值(B) / 收盤價(元)) x (1+(常續性稅後淨利 / 股東權益總額)) ^ 20
        factor_df['GVI'] = df[i_list[3]] / df[i_list[20]] * (1 + (df[i_list[1]] / df[i_list[2]])) ** 20
        # EPS: 每股盈餘
        factor_df['EPS'] = df[i_list[4]]
        """
        # MOM: 報酬率(季)
        factor_df['MOM'] = df[i_list[23]]
        """
        # PE: 本益比-TSE
        factor_df['PE'] = df[i_list[22]]
        # EV_EBITDA: (季底普通股市值 + 淨負債) / 稅前息前折舊前淨利
        factor_df['EV_EBITDA'] = (df[i_list[5]] + df[i_list[6]]) / df[i_list[7]]
        # EV_S: (季底普通股市值 + 淨負債) / 營業收入淨額
        factor_df['EV_S'] = (df[i_list[5]] + df[i_list[6]]) / df[i_list[8]]
        # FCF_P: 自由現金流量(D) / 季底普通股市值
        factor_df['FCF_P'] = df[i_list[9]] / df[i_list[5]]
        # CROIC: 自由現金流量(D) / 負債及股東權益總額
        factor_df['CROIC'] = df[i_list[9]] / df[i_list[10]]
        # FCF_OI: 自由現金流量(D) / 營業收入淨額
        factor_df['FCF_OI'] = df[i_list[9]] / df[i_list[8]]
        # FCF_LTD: 自由現金流量(D) / (特別股負債－非流動 + 應付公司債－非流動 + 銀行借款－非流動 + 其他長期借款－非流動 + FV變動入損益非流動金融負債－指定公平價值－公司債
        df[i_list[11]] = df[i_list[11]].fillna(0)
        df[i_list[12]] = df[i_list[12]].fillna(0)
        df[i_list[13]] = df[i_list[13]].fillna(0)
        df[i_list[14]] = df[i_list[14]].fillna(0)
        df[i_list[19]] = df[i_list[19]].fillna(0)
        LTD_df = df[i_list[11]] + df[i_list[12]] + df[i_list[13]] + df[i_list[14]] + df[i_list[19]]
        LTD_df = LTD_df.astype(np.float)
        df[i_list[9]] = df[i_list[9]].astype(np.float)
        factor_df['FCF_LTD'] = df[i_list[9]].divide(LTD_df) 
        factor_df['FCF_LTD'] = factor_df['FCF_LTD'].replace(np.inf, 0)
        # ROE: 常續性稅後淨利 / 股東權益總額
        factor_df['ROE'] = df[i_list[1]] / df[i_list[2]]
        # ROIC: 常續性稅後淨利 / 負債及股東權益總額
        factor_df['ROIC'] = df[i_list[1]] / df[i_list[10]]
        # P_B: 收盤價(元) / 每股淨值(B)
        factor_df['P_B'] = df[i_list[20]] / df[i_list[3]]
        # Economic profit: 營業收入淨額 - 營業成本
        factor_df['EP'] = df[i_list[8]] - df[i_list[15]]
        # P_S: 季底普通股市值 / 營業收入淨額
        factor_df['P_S'] = df[i_list[5]] / df[i_list[8]]
        # P_IC: 季底普通股市值 / 負債及股東權益總額
        factor_df['P_IC'] = df[i_list[5]] / df[i_list[10]]
        # FC+DY: 自由現金流量(D) + 期末普通股─現金股利 + 期末特別股─現金股利
        factor_df['FCF+DY'] = df[i_list[9]] + df[i_list[16]] + df[i_list[17]]
        # OCF_E: 來自營運之現金流量 / 股東權益總額
        factor_df['OCF_E'] = df[i_list[18]] / df[i_list[2]]
        # FCFPS: 自由現金流量(D) / 流通在外股數(千股)
        factor_df['FCFPS'] = df[i_list[9]] / df[i_list[21]]
        
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
# factor_dict = cal_factor_data()
# write_data_to_mysql(db_name[3], factor_dict)
