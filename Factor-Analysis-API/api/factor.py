import json
import pandas as pd
from flask import jsonify
from flask_restful import Resource
from flask_restful import request
from datetime import datetime
from utils.dbmgr import DBMgr


DB_NAME = 'factor'


class ConnDB:

    def __init__(self):
        self.dbmgr = DBMgr(db=DB_NAME)


class FacListApi(Resource):

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


class FacByTickerApi(Resource):

    def get(self):
        output = []
        try:
            ticker = request.args.get('ticker')

            sql = "SELECT * FROM `{}`".format(ticker)
            args = {}
            status, row, result = ConnDB().dbmgr.query(sql, args, fetch='all')
            
            return jsonify({"result": result})

        except Exception as e:
            print("[Error]: {}".format(e))
            return jsonify({"Error": e})
            pass


class FacByTickerFeildApi(Resource):

    def get(self):
        try:
            ticker = request.args.get('ticker')
            field = request.args.getlist('field')
            # 將 field 變成中間以逗號間隔的字串
            field = [elm + ", " for elm in field]
            field[-1] = field[-1].split(",")[0]
            field = "".join(field)
            
            sql = "SELECT date, {} FROM `{}`".format(field, ticker)
            args = {}
            status, row, result = ConnDB().dbmgr.query(sql, args, fetch='all')
            
            return jsonify({"result": result})

        except Exception as e:
            print("[Error]: {}".format(e))
            return jsonify({"Error": e})
            pass


class FacByDateFeildApi(Resource):

    def get(self):
        try:
            date = request.args.get('date')
            field = request.args.getlist('field')
            # 將 field 變成中間以逗號間隔的字串
            field = [elm + ", " for elm in field]
            field[-1] = field[-1].split(",")[0]
            field = "".join(field)

            # 抓該資料庫底下的所有table名稱
            sql = " SELECT TABLE_NAME \
                    FROM INFORMATION_SCHEMA.TABLES \
                    WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA='{}'".format(DB_NAME)
            args = {}
            status, row, result = ConnDB().dbmgr.query(sql, args, fetch='all')
            
            table_list = []
            for value in result:
                table_list.append(value['TABLE_NAME'])

            # 用 union all 把同一個日子的哪些因子從全部資料表撈出來
            sql = ""
            for ticker in table_list:
                if ticker != table_list[-1]:
                    sql += "SELECT {} FROM `{}` WHERE date = '{}' union all ".format(field, ticker, date)
                else:
                    sql += "SELECT {} FROM `{}` WHERE date = '{}'".format(field, ticker, date)
            status, row, result = ConnDB().dbmgr.query(sql, args, fetch='all')

            # 因為資料表中沒有存股票編號 所以需要手動塞進去
            output = []
            for i, elm in enumerate(result):
                elm['ticker'] = table_list[i]
                output.append(elm)

            return jsonify({"result": output})

        except Exception as e:
            print("[Error]: {}".format(e))
            return jsonify({"Error": e})
            pass
