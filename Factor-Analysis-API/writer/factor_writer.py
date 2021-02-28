import math
import pandas as pd
import numpy as np
# 寫入DF到資料庫用這個套件比較好用
from utils.db import ConnMysql
from utils.config import Config


IND_LIST = [
    '常續性稅後淨利', '股東權益總額', '每股淨值(B)', '每股盈餘', # 0 1 2 3
    '季底普通股市值', '淨負債', '稅前息前折舊前淨利', '營業收入淨額', # 4 5 6 7
    '自由現金流量(D)', '負債及股東權益總額', '特別股負債－非流動', '應付公司債－非流動', # 8 9 10 11
    '銀行借款－非流動', '其他長期借款－非流動', '營業成本', '期末普通股－現金股利', # 12 13 14 15
    '期末特別股－現金股利', '來自營運之現金流量', 'FV變動入損益非流動金融負債－指定公平價值－公司債', '收盤價(元)', # 16 17 18 19
    '流通在外股數(千股)', '本益比-TSE', 'MOM(7個月相對強弱)', 'MOM(52週價格範圍)' # 20 21 22 23
]

class FactorWriter:

    def __init__(self):
        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_share_folder')
        self._path = self._path + 'indicator/'

        self._mydb = ConnMysql()

        factor_dict = self._cal_factor_data()
        self._write_data_to_db(factor_dict)

    def _read_indicator(self, ticker):
        print('read ', ticker)
        conn = self._mydb.connect_db('indicator')
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
    
    def _cal_factor_data(self):
        factor_dict = {}
        conn = self._mydb.connect_db('indicator')
        for ticker in conn.table_names():
            factor_df = pd.DataFrame()
            df = self._read_indicator(ticker)
            factor_df['date'] = df['date']
            # GVI: (每股淨值(B) / 收盤價(元)) x (1+(常續性稅後淨利 / 股東權益總額)) ^ 20
            factor_df['GVI'] = df[IND_LIST[2]] / df[IND_LIST[19]] * (1 + (df[IND_LIST[0]] / df[IND_LIST[1]])) ** 20
            # EPS: 每股盈餘
            factor_df['EPS'] = df[IND_LIST[3]]
            """
            # MOM: 報酬率(季)
            factor_df['MOM'] = df[IND_LIST[23]]
            """
            # PE: 本益比-TSE
            factor_df['PE'] = df[IND_LIST[21]]
            # EV_EBITDA: (季底普通股市值 + 淨負債) / 稅前息前折舊前淨利
            factor_df['EV_EBITDA'] = (df[IND_LIST[4]] + df[IND_LIST[5]]) / df[IND_LIST[6]]
            # EV_S: (季底普通股市值 + 淨負債) / 營業收入淨額
            factor_df['EV_S'] = (df[IND_LIST[4]] + df[IND_LIST[5]]) / df[IND_LIST[7]]
            # FCF_P: 自由現金流量(D) / 季底普通股市值
            factor_df['FCF_P'] = df[IND_LIST[8]] / df[IND_LIST[4]]
            # CROIC: 自由現金流量(D) / 負債及股東權益總額
            factor_df['CROIC'] = df[IND_LIST[8]] / df[IND_LIST[9]]
            # FCF_OI: 自由現金流量(D) / 營業收入淨額
            factor_df['FCF_OI'] = df[IND_LIST[8]] / df[IND_LIST[7]]
            # FCF_LTD: 自由現金流量(D) / (特別股負債－非流動 + 應付公司債－非流動 + 銀行借款－非流動 + 其他長期借款－非流動 + FV變動入損益非流動金融負債－指定公平價值－公司債
            df[IND_LIST[10]] = df[IND_LIST[10]].fillna(0)
            df[IND_LIST[11]] = df[IND_LIST[11]].fillna(0)
            df[IND_LIST[12]] = df[IND_LIST[12]].fillna(0)
            df[IND_LIST[13]] = df[IND_LIST[13]].fillna(0)
            df[IND_LIST[18]] = df[IND_LIST[18]].fillna(0)
            LTD_df = df[IND_LIST[10]] + df[IND_LIST[11]] + df[IND_LIST[12]] + df[IND_LIST[13]] + df[IND_LIST[18]]
            LTD_df = LTD_df.astype(np.float)
            df[IND_LIST[8]] = df[IND_LIST[8]].astype(np.float)
            factor_df['FCF_LTD'] = df[IND_LIST[8]].divide(LTD_df) 
            factor_df['FCF_LTD'] = factor_df['FCF_LTD'].replace(np.inf, 0)
            # ROE: 常續性稅後淨利 / 股東權益總額
            factor_df['ROE'] = df[IND_LIST[0]] / df[IND_LIST[1]]
            # ROIC: 常續性稅後淨利 / 負債及股東權益總額
            factor_df['ROIC'] = df[IND_LIST[0]] / df[IND_LIST[9]]
            # P_B: 收盤價(元) / 每股淨值(B)
            factor_df['P_B'] = df[IND_LIST[19]] / df[IND_LIST[2]]
            # EP: 營業收入淨額 - 營業成本
            factor_df['EP'] = df[IND_LIST[7]] - df[IND_LIST[14]]
            # P_S: 季底普通股市值 / 營業收入淨額
            factor_df['P_S'] = df[IND_LIST[4]] / df[IND_LIST[7]]
            # P_IC: 季底普通股市值 / 負債及股東權益總額
            factor_df['P_IC'] = df[IND_LIST[4]] / df[IND_LIST[9]]
            # FCF_DY: 自由現金流量(D) + 期末普通股─現金股利 + 期末特別股─現金股利
            factor_df['FCF_DY'] = df[IND_LIST[8]] + df[IND_LIST[15]] + df[IND_LIST[16]]
            # OCF_E: 來自營運之現金流量 / 股東權益總額
            factor_df['OCF_E'] = df[IND_LIST[17]] / df[IND_LIST[1]]
            # FCFPS: 自由現金流量(D) / 流通在外股數(千股)
            factor_df['FCFPS'] = df[IND_LIST[8]] / df[IND_LIST[20]]
            # MOM_7m: 7個月相對強弱 = (目前股價 - 7個月前股價) / 7個月前股價
            factor_df['MOM_7m'] = df[IND_LIST[22]]
            # MOM_52w_PR: 52週價格範圍 = (目前股價 - 52週內最低價) / (52週內最高價 - 52週內最低價)
            factor_df['MOM_52w_PR'] = df[IND_LIST[23]]
            
            # 除數為0導致出現inf
            factor_df = factor_df.replace([np.inf, -np.inf], np.nan)
            factor_dict[ticker] = factor_df
        return factor_dict

    def _write_data_to_db(self, ticker_data_dict):
        conn = self._mydb.connect_db('factor')
        for key, value in ticker_data_dict.items():
            value.to_sql(key, con=conn)
            print('successfully write '+key+' to db')
