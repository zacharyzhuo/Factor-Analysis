import pandas as pd
from flask import jsonify
from flask_restful import Resource
from flask_restful import request
from datetime import datetime
from utils.db import ConnMysql


mydb = ConnMysql()
db_name = "stock"
conn = mydb.connect_db(db_name)


class StkListApi(Resource):

    def get(self):
        table_name_list = conn.table_names()
        return jsonify({"result": table_name_list})


class StkByTickerApi(Resource):

    def get(self):
        output = {}
        try:
            ticker_list = request.args.getlist('ticker_list')
            for ticker in ticker_list:
                sql = "SELECT * FROM `{}`".format(ticker)
                stks = conn.execute(sql)
                ticker_data_list = []
                if stks:
                    for stk in stks:
                        stk_dict = dict(stk)
                        del stk_dict["index"]
                        ticker_data_list.append(stk_dict)
                output[ticker] = ticker_data_list
        except Exception as e:
            output = "No such ticker"
            print(e)
        return jsonify({"result": output})


class StkByTickerDateApi(Resource):

    def get(self):
        output = {}
        try:
            ticker_list = request.args.getlist('ticker_list')
            date = request.args.get('date')
            date = date.split("-")
            start_date = date[0]
            end_date = date[1]
            dates_list = pd.date_range(start_date, end_date).tolist()
            dates_list = [date_obj.strftime("%Y-%m-%d")
                          for date_obj in dates_list]
            for ticker in ticker_list:
                sql = "SELECT * FROM `{}`".format(ticker)
                stks = conn.execute(sql)
                ticker_data_list = []
                if stks:
                    for stk in stks:
                        stk_dict = dict(stk)
                        if stk_dict["date"] in dates_list:
                            del stk_dict["index"]
                            ticker_data_list.append(stk_dict)
                output[ticker] = ticker_data_list
        except Exception as e:
            output = "Please enter the correct date range format. \
                    (e.g. 20190322-20200322) Note: earliest date 20000101; latest date 20201101"
            print(e)
            pass
        return jsonify({"result": output})
