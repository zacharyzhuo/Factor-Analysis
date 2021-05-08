import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.dbmgr import DBMgr
from utils.config import Config
from service.calendar import Calendar


class MOMCalculator:

    def __init__(self):
        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_share_folder') + 'indicator/'
        self._dbmgr = DBMgr(db='indicator')
        self._cal = Calendar('TW')

        self._df, ori_column_list, title_list = self._init_result_format()
        self._cal_related_mom()
        self._output_excel(self._df, ori_column_list, title_list)

    def _init_result_format(self):
        df = pd.read_excel(self._path+'本益比-TSE.xlsx')
        ori_column_list = df.columns

        column_list = [x.split(" ")[0] for x in list(df.columns)]
        df.columns = column_list

        title_list = ["MOM(季)" for x in df.iloc[0].tolist()]

        df = df.iloc[1:]
        df.rename(columns={'Unnamed:': 'date'}, inplace=True)
        df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d").astype(str)
        df = df.sort_values(by=['date']).set_index('date')
        
        return df, ori_column_list, title_list

    def _cal_related_mom(self):
        column_list = self._df.columns.tolist()
        date_list = self._df.index.tolist()
        dbmgr = DBMgr(db='stock')
        
        for ticker in column_list:
            print('ticker: ', ticker)
            ticker = str(ticker)
            temp_df = pd.DataFrame(date_list, columns=['date'])
            
            sql = "SELECT * FROM `{}`".format(ticker)
            args = {}
            status, row, result = dbmgr.query(sql, args)
            stk_df = pd.DataFrame(result).set_index('date')[['close']]

            temp_df['report_date'] = temp_df['date'].apply(
                lambda date: self._cal.get_report_date(date, 1) if date.split("-")[1] == '03' else self._cal.get_report_date(date, 0)
            )
            temp_df['price_1'] = temp_df['date'].apply(lambda date: stk_df.loc[date]['close'])
            temp_df['price_2'] = temp_df['report_date'].apply(lambda date: np.nan if date == 0 else stk_df.loc[date]['close'])
            temp_df[ticker] = (temp_df['price_1'] - temp_df['price_2']) / temp_df['price_2']
            temp_df = temp_df.set_index('date')[[ticker]]
            print(temp_df)
            self._df[ticker] = temp_df[ticker]

    def _output_excel(self, df, ori_column_list, title_list):
        ori_column_list = list(ori_column_list)
        ori_column_list.pop(0)
        df.columns = ori_column_list

        title_list.pop(0)
        first_row = pd.DataFrame([title_list], columns=ori_column_list)

        df = df.sort_index(ascending=False)
        df.index.names = ['']
        df = pd.concat([first_row, df])
        df.to_excel('MOM(季).xlsx', header=True, encoding="utf_8_sig")
