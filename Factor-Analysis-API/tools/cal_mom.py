import pandas as pd
import numpy as np
import time
import datetime
import math
from datetime import datetime, timedelta
import requests
import json
import sys
sys.path.append("../")
from utils.db import ConnMysql
from utils.config import Config


mydb = ConnMysql()
db_name = "calendar"
conn = mydb.connect_db(db_name)

server_ip = "http://140.115.87.197:8090/"

class Calendar:

    def __init__(self, country):
        self.country = country

        self._cfg = Config()
        
        self.df = self.read_calendar()

    def read_calendar(self):
        try:
            sql = "SELECT * FROM `{}`".format(self.country)
            cals = conn.execute(sql)
            df = pd.DataFrame(cals.fetchall())
            df.columns = cals.keys()
            df = df.drop(columns=['index'])
            return df
        except Exception as e:
            print(e)


def get_trade_date(country, date, how, freq):
        try:
            df = Calendar(country).df
            how = (abs(int(how)) + 1) *-1
            freq = freq.lower()
            if type(date) is str:
                date = datetime.strptime(date, "%Y-%m-%d")
            start_date = df['date'].iloc[0]
            date_df = df.loc[df['date'] <= date]
            selected_date = date_df['date'].iloc[-1]

            if freq == 'd':
                output_date = date_df.iloc[how]

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
                output_date = result_df.iloc[how]

            elif freq == 's':
                result_df = pd.DataFrame()
                season_month = [3, 6, 9, 12]
                for i in range(start_date.year, selected_date.year + 1):
                    for j in season_month:
                        if i == selected_date.year and selected_date.month < j:
                            pass
                        else:
                            if j == 12:
                                dt_end = (datetime(i, 12, 31)).strftime("%Y-%m-%d")
                            else:
                                dt_end = (datetime(i, j+1, 1) - timedelta(days=1)).strftime("%Y-%m-%d")
                            season_end_df = date_df.loc[date_df['date'] <= dt_end]
                            season_end = season_end_df.iloc[-1]
                            result_df = result_df.append(season_end, ignore_index=True)
                output_date = result_df.iloc[how]

            elif freq == 'y':
                result_df = pd.DataFrame()
                for i in range(start_date.year, selected_date.year + 1):
                    if i == selected_date.year:
                        pass
                    else:
                        dt_end = (datetime(i, 12, 31)).strftime("%Y-%m-%d")
                        year_end_df = date_df.loc[date_df['date'] <= dt_end]
                        year_end = year_end_df.iloc[-1]
                        result_df = result_df.append(year_end, ignore_index=True)
                output_date = result_df.iloc[how]

            output_date = output_date['date'].strftime('%Y-%m-%d')
        except Exception as e:
            print(e)
            pass
        return output_date

def get_report_date(country, date):
        try:
            report_date_list = ['05-15', '08-14', '11-14', '03-31']

            df = Calendar(country).df
            if type(date) is str:
                date = datetime.strptime(date, "%Y-%m-%d")
            year = date.year
            momth = date.month
            for i in range(len(report_date_list)):
                if i == 3 and momth > 3:
                    report_date_list[i] = str(year+1) + "-" + report_date_list[i]
                else:
                    report_date_list[i] = str(year) + "-" + report_date_list[i]
                report_date_list[i] = datetime.strptime(report_date_list[i], "%Y-%m-%d")
                if df['date'].iloc[-1] < report_date_list[i]:
                    report_date_list[i] = None
                else:
                    report_date_df = df.loc[df['date'] <= report_date_list[i]]
                    report_date_list[i] = report_date_df['date'].iloc[-1]
                
            report_date_list = list(filter(None, report_date_list))
            report_date_list.sort()
            for elm in report_date_list:
                if date < elm:
                    output_date = elm
                    break
            output_date = output_date.strftime('%Y-%m-%d')
        except Exception as e:
            print(e)
            pass
        return output_date

def read_excel_template():
    df = pd.read_excel('../data/raw_data/indicator/上市上櫃_回報率(季).xlsx')
    original_column_list = df.columns
    column_list = list(df.columns)
    column_list = [x.split(" ")[0] for x in column_list]
    df.columns = column_list
    first_row_list = df.iloc[0].tolist()
    for i in range(len(first_row_list)):
        first_row_list[i] = '報酬率(季)'
    df = df.iloc[1:]
    df.rename(columns={'Unnamed:': 'date'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d").astype(str)
    df = df.sort_values(by=['date'])
    df = df.set_index('date')
    return df, original_column_list, first_row_list

def cal_mom(df):
    for ticker in list(df.columns):
        print('ticker: ', ticker)
        ticker_list = [ticker]
        payloads = {
            'ticker_list': ticker_list,
        }
        response = requests.get(server_ip+"stk/get_ticker_all_stk", params=payloads)
        stk = json.loads(response.text)['result']
        stk = stk[ticker_list[0]]
        stk_df = pd.DataFrame(stk)
        stk_df = stk_df[['date', 'close']]
        for date, _ in df.loc[:, ticker].items():
            try:
                pre_season_date = get_trade_date('TW', date, '1', 's')
                report_date = get_report_date('TW', date)
                pre_season_stk = stk_df.loc[stk_df['date'] == pre_season_date]['close'].values[0]
                report_date_stk = stk_df.loc[stk_df['date'] == report_date]['close'].values[0]
                return_rate = (report_date_stk - pre_season_stk) / pre_season_stk * 100
                df.loc[date, ticker] = return_rate
            except Exception as e:
                print(e)
                return_rate = np.nan
                df.loc[date, ticker] = return_rate
        print(df.loc[:, ticker])
    return df
  
def output_excel(df, original_column_list, first_row_list):
    original_column_list = list(original_column_list)
    original_column_list.pop(0)
    df.columns = original_column_list
    first_row_list.pop(0)
    first_row = pd.DataFrame([first_row_list], columns=original_column_list)
    df = df.sort_index(ascending=False)
    df.index.names = ['']
    df = pd.concat([first_row, df])
    df.to_excel('上市上櫃_回報率(季).xlsx', header=True, encoding="utf_8_sig")


start = time.time()
df, original_column_list, first_row_list = read_excel_template()
df = cal_mom(df)
output_excel(df, original_column_list, first_row_list)

end = time.time()
print("Execution time: %f second" % (end - start))
