import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from utils.config import Config


class Calendar:

    def __init__(self, country):
        self._country = country

        self._cfg = Config()
        self._api_server_IP = self._cfg.get_value('IP', 'api_server_IP')

        self._date_df = self._get_all_trade_day()

    def _get_all_trade_day(self):
        # 預載歷史每天交易日日期
        payloads = {
            'country': self._country,
        }
        response = requests.get("http://{}/cal/get_all_date".format(self._api_server_IP), params=payloads)
        date_list = json.loads(response.text)['result']
        date_df = pd.DataFrame(date_list, columns=['date'])
        date_df['date'] = pd.to_datetime(date_df['date'], format="%Y-%m-%d")
        return date_df

    # 往前抓交易日
    # input: date   : 以某天為基準
    #        how    : 往前數多少單位
    #        freq   : (顆粒度) d:日 m:月 s:季 y:年
    def advance_date(self, date, how, freq):
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
            result_date = date_df.iloc[how]

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
            result_date = result_df.iloc[how]

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
            result_date = result_df.iloc[how]

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
            result_date = result_df.iloc[how]

        result_date = result_date['date'].strftime('%Y-%m-%d')
        return result_date    

    # 抓出指定日期內所有財報公布日
    # input: start_date   : 開始日
    #        end_date     : 結束日
    def get_report_date_list(self, start_date, end_date):
        try:
            report_date_list = ['03-31', '05-15', '08-14', '11-14']
            df = self._date_df
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

    # 往前或者往後抓幾個財報公布日
    # input: date   : 基準日
    #        how    : 單位
    def get_report_date(self, date, how):
        try:
            if type(date) is not str:
                date = date.strftime('%Y-%m-%d')
            # 預設為資料庫歷史資料最大區間
            report_date_list = self.get_report_date_list('2000-01-01', '2020-12-31')
            result_list = []
            for report_date in report_date_list:
                if how < 0:
                    if report_date < date:
                        result_list.append(report_date)
                else:
                    if report_date >= date:
                        result_list.append(report_date)
        except Exception as e:
            print(e)
            pass
        return result_list[how]
