import pandas as pd
import numpy as np
import datetime
# import sys
# sys.path.append("../")
from utils.dbmgr import DBMgr
from utils.config import Config


class CalendarWriter:

    def __init__(self):
        self._cfg = Config()
        self._dbmgr = DBMgr()

        self._path = self._cfg.get_value('path', 'path_to_share_folder')

    def _read_file(self):
        calendar_dict = {}
        
        df = pd.read_excel(row_data_path[0]+country_list[0]+'_calendar.xlsx')
        df = df[['年月日']].sort_values(by='年月日').reset_index(drop=True)
        df.columns = ['date']
        calendar_dict[country_list[0]] = df
        return calendar_dict

# """
# tej smart wizard
# 股價資料庫
# 資料格式: 預設
# """

# row_data_path = ['../data/raw_data/calendar/']
# country_list = ['tw']

# mydb = ConnMysql()
# db_name = ['stock', 'stock_index', 'indicator', 'factor', 'ranked_factor', 'calendar']


# def write_tw_calendar():
#     calendar_dict = {}
#     df = pd.read_excel(row_data_path[0]+country_list[0]+'_calendar.xlsx')
#     df = df[['年月日']].sort_values(by='年月日').reset_index(drop=True)
#     df.columns = ['date']
#     calendar_dict[country_list[0]] = df
#     return calendar_dict

# def write_data_to_mysql(db_name, calendar_dict):
#     conn = mydb.connect_db(db_name)
#     for key, value in calendar_dict.items():
#         value.to_sql(key, con=conn)
#         print('successfully write '+key+' to db')


# calendar_dict = write_tw_calendar()
# write_data_to_mysql(db_name[5], calendar_dict)