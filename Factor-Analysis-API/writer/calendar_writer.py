import pandas as pd
from utils.dbmgr import DBMgr
from utils.config import Config


class CalendarWriter:

    def __init__(self):
        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_share_folder') + 'calendar/'

        self._dbmgr = DBMgr(db='calendar')

        df = self._read_file()
        self._write_data_to_db(df)

    def _read_file(self):
        df = pd.read_excel(self._path+'tw_calendar.xlsx')
        df = df[['年月日']].sort_values(by='年月日').reset_index(drop=True)
        df.columns = ['date']
        return df

    def _write_data_to_db(self, df):
        # 不知道為啥create table & insert要分開來寫才行
        sql = " drop table if exists `tw`;"
        args = {}
        status, row, result = self._dbmgr.insert(sql, args)

        sql = " CREATE TABLE `tw`( \
                `id` int(5) PRIMARY KEY AUTO_INCREMENT NOT NULL, \
                `date` datetime COLLATE utf8mb4_unicode_ci \
                )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        args = {}
        status, row, result = self._dbmgr.insert(sql, args)
                
        sql = " INSERT INTO `tw` \
                VALUES      ('0', %(date)s)"
        args = df.to_dict('records')
        status, row, result = self._dbmgr.insert(sql, args, multiple=True)
