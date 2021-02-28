import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pathos
from multiprocessing import Pool
from utils.dbmgr import DBMgr
from utils.config import Config


class MOMCalculator:

    FILE_NAME_1 = 'MOM(7個月相對強弱)'
    FILE_NAME_2 = 'MOM(52週價格範圍)'

    def __init__(self):
        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_share_folder')

        self._dbmgr = DBMgr(db='indicator')

        self._date_df = self._get_calendar()

        # self._df, ori_column_list, title_list = self._init_result_format(MOMCalculator.FILE_NAME_1)
        # self._cal_related_mom()
        # self._output_excel(self._df, ori_column_list, title_list, MOMCalculator.FILE_NAME_1)

        self._df, ori_column_list, title_list = self._init_result_format(MOMCalculator.FILE_NAME_2)
        self._cal_price_range()
        self._output_excel(self._df, ori_column_list, title_list, MOMCalculator.FILE_NAME_2)

    def _get_calendar(self):
        dbmgr = DBMgr(db='calendar')
        sql = "SELECT * FROM `{}`".format('tw')
        args = {}
        status, row, result = dbmgr.query(sql, args)
        date_df = pd.DataFrame(result).drop(columns=['index'])
        return date_df

    def _init_result_format(self, title):
        df = pd.read_excel(self._path+'indicator/本益比-TSE.xlsx')
        ori_column_list = df.columns
        column_list = list(df.columns)
        column_list = [x.split(" ")[0] for x in column_list]
        df.columns = column_list
        title_list = df.iloc[0].tolist()
        for i in range(len(title_list)):
            title_list[i] = title
        df = df.iloc[1:]
        df.rename(columns={'Unnamed:': 'date'}, inplace=True)
        df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d").astype(str)
        df = df.sort_values(by=['date']).set_index('date')
        return df, ori_column_list, title_list

    def _get_advance_date(self, date, how, freq):
        try:
            df = self._date_df
            how = (abs(int(how)) + 1) *-1
            freq = freq.lower()
            if type(date) is str:
                date = datetime.strptime(date, "%Y-%m-%d")
            # 歷史資料最早的那天
            start_date = df['date'].iloc[0]
            # 抓出比參數(date)更早或等於的交易日
            date_df = df.loc[df['date'] <= date]
            # 最接近參數(date)的交易日
            selected_date = date_df['date'].iloc[-1]

            if freq == 'd':
                output_date = date_df.iloc[how]['date'].strftime('%Y-%m-%d')

            elif freq == 'm':
                result_df = pd.DataFrame()
                for i in range(start_date.year, selected_date.year + 1):
                    for j in range(1, 13):
                        selected_date_add_one_day = (selected_date + timedelta(days=1)).strftime('%Y-%m-%d')
                        org_month = selected_date.strftime('%Y-%m-%d').split("-")[1]
                        add_one_day_month = selected_date_add_one_day.split("-")[1]
                        if i == selected_date.year and selected_date.month < j:
                            pass
                        elif i == selected_date.year and selected_date.month == j and org_month == add_one_day_month:
                            pass
                        else:
                            if j == 12:
                                dt_end = (datetime(i, 12, 31)).strftime("%Y-%m-%d")
                            else:
                                dt_end = (datetime(i, j+1, 1) - timedelta(days=1)).strftime("%Y-%m-%d")
                            month_end_df = date_df.loc[date_df['date'] <= dt_end]
                            month_end = month_end_df.iloc[-1]
                            result_df = result_df.append(month_end, ignore_index=True)
                output_date = result_df.iloc[how]['date'].strftime('%Y-%m-%d')
        except Exception as e:
            output_date = 0
        return output_date

    def _get_price_in_52w(self, stk_df, date, column):
        try:
            date_df = self._date_df
            if type(date) is str:
                temp_date = datetime.strptime(date, "%Y-%m-%d")
                
            the_day_b4_52w = (temp_date - timedelta(days=7*52)).strftime('%Y-%m-%d')
            the_day_b4_52w = self._get_advance_date(the_day_b4_52w, 0, 'd')
            stk_df = stk_df.loc[(stk_df['date'] >= the_day_b4_52w) & (stk_df['date'] <= date)]

            if column == 'high':
                price = stk_df['high'].max()
            elif column == 'low':
                price = stk_df['low'].min()
        except Exception as e:
            price = np.nan
        return price

    def _cal_related_mom(self):
        column_list = self._df.columns.tolist()
        date_list = self._df.index.tolist()
        dbmgr = DBMgr(db='stock2')
        
        for ticker in column_list:
            print('ticker: ', ticker)
            ticker = str(ticker)
            temp_df = pd.DataFrame(date_list, columns=['date'])
            
            sql = "SELECT * FROM `{}`".format(ticker)
            args = {}
            status, row, result = dbmgr.query(sql, args)
            stk_df = pd.DataFrame(result).set_index('date')[['close']]

            temp_df['seven_m_ago'] = temp_df['date'].apply(lambda date: self._get_advance_date(date, 7, 'm'))
            temp_df['price_1'] = temp_df['date'].apply(lambda date: stk_df.loc[date]['close'])
            temp_df['price_2'] = temp_df['seven_m_ago'].apply(lambda date: np.nan if date == 0 else stk_df.loc[date]['close'])
            temp_df[ticker] = (temp_df['price_1'] - temp_df['price_2']) / temp_df['price_2']
            temp_df = temp_df.set_index('date')[[ticker]]
            self._df[ticker] = temp_df[ticker]

        # 使用 inner function 特別獨立出需要多核運算的部分
        # def multiprocessing_job(ticker):
        # # for ticker in column_list:
        #     print('ticker: ', ticker)
        #     ticker = str(ticker)
        #     temp_df = pd.DataFrame(date_list, columns=['date'])
        #     temp_df['seven_m_ago'] = temp_df['date'].apply(lambda date: self._get_advance_date(date, 7))
            
        #     sql = "SELECT * FROM `{}`".format(ticker)
        #     args = {}
        #     status, row, result = dbmgr.query(sql, args)
        #     stk_df = pd.DataFrame(result).set_index('date')[['close']]
        #     temp_df['price_1'] = temp_df['date'].apply(lambda date: stk_df.loc[date]['close'])
        #     temp_df['price_2'] = temp_df['seven_m_ago'].apply(lambda date: np.nan if date == 0 else stk_df.loc[date]['close'])
        #     temp_df[ticker] = (temp_df['price_1'] - temp_df['price_2']) / temp_df['price_2']
        #     temp_df = temp_df.set_index('date')[[ticker]]
        #     self._df[ticker] = temp_df[ticker]
        #     # return {ticker: temp_df[ticker]}
        
        # # 因為有使用 inner function 所以要使用 pathos 的 multiprocessing 而非 python 原生的
        # # Pool() 不放參數則默認使用電腦核的數量
        # pool = pathos.multiprocessing.Pool()
        # results = pool.map(multiprocessing_job, column_list) 
        # pool.close()
        # pool.join()

        # for result in results:
        #     if result:
        #         self._df[list(result.keys())[0]] = list(result.values())[0]

    def _cal_price_range(self):
        column_list = self._df.columns.tolist()
        date_list = self._df.index.tolist()
        dbmgr = DBMgr(db='stock2')

        for ticker in column_list:
            print('ticker: ', ticker)
            temp_df = pd.DataFrame(date_list, columns=['date'])
            
            sql = "SELECT * FROM `{}`".format(ticker)
            args = {}
            status, row, result = dbmgr.query(sql, args)
            stk_df = pd.DataFrame(result)

            temp_df['price'] = temp_df['date'].apply(lambda date: stk_df.loc[stk_df['date'] == date]['close'].values[0])
            temp_df['high_in_52w'] = temp_df['date'].apply(lambda date: self._get_price_in_52w(stk_df, date, 'high'))
            temp_df['low_in_52w'] = temp_df['date'].apply(lambda date: self._get_price_in_52w(stk_df, date, 'low'))
            temp_df[ticker] = (temp_df['price'] - temp_df['low_in_52w']) / (temp_df['high_in_52w'] - temp_df['low_in_52w'])
            temp_df = temp_df.set_index('date')[[ticker]]
            self._df[ticker] = temp_df[ticker]

    def _output_excel(self, df, ori_column_list, title_list, file_name):
        ori_column_list = list(ori_column_list)
        ori_column_list.pop(0)
        df.columns = ori_column_list
        title_list.pop(0)
        first_row = pd.DataFrame([title_list], columns=ori_column_list)
        df = df.sort_index(ascending=False)
        df.index.names = ['']
        df = pd.concat([first_row, df])
        df.to_excel(file_name+'.xlsx', header=True, encoding="utf_8_sig")
