import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from utils.config import Config


SEASON_MONTH = [3, 6, 9, 12]


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

    # 往前或往後抓交易日
    # input: date   : 以某天為基準
    #        how    : 負數往前 正數往後
    #        freq   : d:日 s:季 
    def get_trade_date(self, date, how, freq):
        df = self._date_df
        if type(date) is str:
            date = datetime.strptime(date, "%Y-%m-%d")

        if freq.lower() == 'd':
            date_df = df.loc[df['date'] <= date] if how < 0 else df.loc[df['date'] >= date]
            return date_df.iloc[how]['date'].strftime('%Y-%m-%d')

        elif freq.lower() == 's':
            year = date.year

            # 往前
            if how < 0:
                # 往前找最接近的 3 6 9 12
                temp_list = [season for season in SEASON_MONTH if season < date.month]

                # 如果月份=1或2 也就是最接近的是去前的12月
                if len(temp_list) == 0:
                    year = year - 1
                    month = 12
                else:
                    month = temp_list[-1]
                # 季=3*月 要少扣一個月 因為要用隔月的1號-1天去抓該月的月底
                temp_date = datetime(year, month, 1) - relativedelta(months=3*abs(how+1)-1)
                closest_season_date = (temp_date-timedelta(days=1)).strftime("%Y-%m-%d")
                closest_season_df = df.loc[df['date'] <= closest_season_date]
                closest_season_date = closest_season_df['date'].iloc[-1]

            # 往後 或=0
            else:
                # 往前找最接近的 3 6 9 12
                temp_list = [season for season in SEASON_MONTH if season > date.month]
                month = temp_list[0]

                # 季=3*月 要多加一個月 因為要用隔月的1號-1天去抓該月的月底
                temp_date = datetime(year, month, 1) + relativedelta(months=3*(how-1)+1)
                closest_season_date = (temp_date-timedelta(days=1)).strftime("%Y-%m-%d")
                closest_season_df = df.loc[df['date'] >= closest_season_date]
                closest_season_date = closest_season_df['date'].iloc[0]
            
            return closest_season_date.strftime('%Y-%m-%d')
        
        elif freq.lower() == 'm' or freq.lower() == 'y':
            if freq.lower() == 'm':
                target_date = date + relativedelta(months=how)

            elif freq.lower() == 'y':
                target_date = datetime(date.year+how, date.month, date.day)
            
            if how < 0:
                target_date_df = df.loc[df['date'] <= target_date]
                target_date = target_date_df['date'].iloc[-1]
            else:
                target_date_df = df.loc[df['date'] >= target_date]
                target_date = target_date_df['date'].iloc[0]
            
            return target_date.strftime('%Y-%m-%d')
    
    def get_period_trade_date(self, start, end):
        df = self._date_df

        if type(start) is str:
            start = datetime.strptime(start, "%Y-%m-%d")
        if type(end) is str:
            end = datetime.strptime(end, "%Y-%m-%d")

        return df.loc[(df['date'] >= start) & (df['date'] <= end)]['date'].to_list()

    # 抓出指定日期內所有財報公布日
    # input: start_date   : 開始日
    #        end_date     : 結束日
    def get_report_date_list(self, start_date, end_date):
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

        return date_list

    # 往前或者往後抓幾個財報公布日
    # input: date   : 基準日
    #        how    : 單位
    def get_report_date(self, date, how):
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

        return result_list[how]
