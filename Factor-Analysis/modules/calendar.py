import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta


server_ip = "http://140.115.87.197:8090/"


class Calendar:
    def __init__(self, country):
        self.country = country
        self.date_df = self.get_all_trade_day()


    def get_all_trade_day(self):
        payloads = {
            'country': 'TW',
        }
        response = requests.get(server_ip+"cal/get_all_date", params=payloads)
        date_list = json.loads(response.text)['result']
        date_df = pd.DataFrame(date_list, columns=['date'])
        date_df['date'] = pd.to_datetime(date_df['date'], format="%Y-%m-%d")
        return date_df


    def advance_date(self, date, how, freq):
        df = self.date_df
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
        return output_date    


    def get_report_date(self, date):
        try:
            report_date_list = ['03-31', '05-15', '08-14', '11-14']
            df = self.date_df

            if type(date) is str:
                date = datetime.strptime(date, "%Y-%m-%d")
            year = date.year
            momth = date.month
            for i in range(len(report_date_list)):
                # 大於3月 年都+1
                if i == 0 and momth > 3:
                    report_date_list[i] = str(year+1) + "-" + report_date_list[i]
                else:
                    report_date_list[i] = str(year) + "-" + report_date_list[i]
                report_date_list[i] = datetime.strptime(report_date_list[i], "%Y-%m-%d")
                # 超過Calendar的日期都拿掉
                if df['date'].iloc[-1] < report_date_list[i]:
                    report_date_list[i] = None
                else:
                    # 將report date轉換成最接近calendar上的交易日
                    report_date_df = df.loc[df['date'] <= report_date_list[i]]
                    report_date_list[i] = report_date_df['date'].iloc[-1]
            
            # 去掉陣列上空的元素
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
    
    
    def get_report_date_list(self, start_date, end_date):
        try:
            report_date_list = ['03-31', '05-15', '08-14', '11-14']
            df = self.date_df
            date_list = []

            if type(start_date) is not str:
                start_date = start_date.strftime('%Y-%m-%d')
            if type(end_date) is not str:
                end_date = end_date.strftime('%Y-%m-%d')
            start_year = int(start_date.split('-')[0])
            end_year = int(end_date.split('-')[0])

            for year in range(start_year, end_year+1):
                for report_date in report_date_list:
                    date = str(year) + '-' + report_date
                    report_date_df = df.loc[df['date'] <= date]
                    date = report_date_df['date'].iloc[-1]
                    date = date.strftime('%Y-%m-%d')
                    # 需要在給定的期間內才append
                    if date >= start_date and date <= end_date:
                        date_list.append(date)
        except Exception as e:
            print(e)
            pass
        return date_list
