import pandas as pd
from flask import jsonify
from flask_restful import Resource
from flask_restful import request
from datetime import datetime
from utils.dbmgr import DBMgr


DB_NAME = 'stock'


class ConnDB:

    def __init__(self):
        self.dbmgr = DBMgr(db=DB_NAME)


class StkListApi(Resource):

    def get(self):
        try:
            # 抓該資料庫底下的所有table名稱
            sql = " SELECT TABLE_NAME \
                    FROM INFORMATION_SCHEMA.TABLES \
                    WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA='{}'".format(DB_NAME)
            args = {}
            status, row, result = ConnDB().dbmgr.query(sql, args, fetch='all')
            
            table_list = []
            for value in result:
                table_list.append(value['TABLE_NAME'])

            return jsonify({"result": table_list})

        except Exception as e:
            print("[Error]: {}".format(e))
            return jsonify({"Error": e})
            pass


class StkByTickerApi(Resource):

    def get(self):
        output = {}
        try:
            ticker_list = request.args.getlist('ticker_list')

            for ticker in ticker_list:
                sql = "SELECT * FROM `{}`".format(ticker)
                args = {}
                status, row, result = ConnDB().dbmgr.query(sql, args, fetch='all')

                output[ticker] = result

            return jsonify({"result": output})

        except Exception as e:
            print("[Error]: {}".format(e))
            return jsonify({"Error": e})
            pass


class StkByTickerDateApi(Resource):

    def get(self):
        output = {}
        try:
            ticker_list = request.args.getlist('ticker_list')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')

            for ticker in ticker_list:
                # 抓限定時間範圍內股價
                sql = " SELECT * FROM `{}` \
                        WHERE `date` >= %(start_date)s \
                        AND `date` <= %(end_date)s".format(ticker)
                args = {'start_date': start_date, 'end_date': end_date}
                status, row, result = ConnDB().dbmgr.query(sql, args, fetch='all')

                output[ticker] = result

            return jsonify({"result": output})

        except Exception as e:
            print("[Error]: {}".format(e))
            return jsonify({"Error": e})
            pass
