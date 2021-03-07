import json
import pandas as pd
import numpy as np
from flask import jsonify
from flask_restful import Resource
from flask_restful import request
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from utils.dbmgr import DBMgr


DB_NAME = 'calendar'
SEASON_MONTH = [3, 6, 9, 12]


class Calendar:

    def __init__(self, country):
        self.country = country

        self._dbmgr = DBMgr(db=DB_NAME)

        self.df = self.read_calendar()

    def read_calendar(self):
        sql = "SELECT * FROM `{}`".format(self.country)
        args = {}
        status, row, result = self._dbmgr.query(sql, args, fetch='all')
        df = pd.DataFrame(result)
        df = df.drop(columns=['index'])

        return df

class AllTradeDateApi(Resource):

    def get(self):
        try:
            country = request.args.get('country')
            df = Calendar(country).df
            date_list = df['date'].dt.strftime('%Y-%m-%d').tolist()

            return jsonify({"result": date_list})

        except Exception as e:
            print("[Error]: {}".format(e))
            return jsonify({"Error": e})
            pass


class TradeDateApi(Resource):

    def get(self):
        try:
            country = request.args.get('country')
            date = request.args.get('date')
            how = int(request.args.get('how'))
            freq = request.args.get('freq').lower()

            df = Calendar(country).df
            if type(date) is str:
                date = datetime.strptime(date, "%Y-%m-%d")

            # 歷史資料最早的那天
            start_date = df['date'].iloc[0]

            date_df = df.loc[df['date'] <= date] if how < 0 else df.loc[df['date'] >= date]

            if freq == 'd':
                return jsonify({"result": date_df.iloc[how]['date'].strftime('%Y-%m-%d')})

            elif freq == 's':
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
                
                return jsonify({"result": closest_season_date.strftime('%Y-%m-%d')})

        except Exception as e:
            print("[Error]: {}".format(e))
            return jsonify({"Error": e})
            pass


class ReportDateListApi(Resource):
    
    def get(self):
        try:
            report_date_list = ['05-15', '08-14', '11-14', '03-31']
            country = request.args.get('country')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')

            df = Calendar(country).df

            if type(start_date) is not str:
                start_date = start_date.strftime('%Y-%m-%d')
            if type(end_date) is not str:
                end_date = end_date.strftime('%Y-%m-%d')
            start_year = int(start_date.split('-')[0])
            end_year = int(end_date.split('-')[0])

            date_list = []
            for year in range(start_year, end_year+1):
                for report_date in report_date_list:
                    date = str(year) + '-' + report_date
                    report_date_df = df.loc[df['date'] <= date]
                    date = report_date_df['date'].iloc[-1]
                    date = date.strftime('%Y-%m-%d')
                    # 需要在給定的期間內才append
                    if date >= start_date and date <= end_date:
                        date_list.append(date)

            return jsonify({"result": date_list})

        except Exception as e:
            print("[Error]: {}".format(e))
            return jsonify({"Error": e})
            pass
