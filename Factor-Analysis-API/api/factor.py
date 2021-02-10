import json
import pandas as pd
from flask import jsonify
from flask_restful import Resource
from flask_restful import request
from datetime import datetime
from utils.db import ConnMysql


mydb = ConnMysql()
db_name = "factor"
conn = mydb.connect_db(db_name)


class FacListApi(Resource):

    def get(self):
        table_name_list = conn.table_names()
        return jsonify({"result": table_name_list})


class FacByTickerApi(Resource):

    def get(self):
        output = []
        try:
            ticker = request.args.get('ticker')
            sql = "SELECT * FROM `{}`".format(ticker)
            facs = conn.execute(sql)
            if facs:
                for fac in facs:
                    fac = dict(fac)
                    del fac["index"]
                    output.append(fac)
        except Exception as e:
            output = "No such ticker"
            print(e)
        return jsonify({"result": output})


class FacByTickerFeildApi(Resource):

    def get(self):
        try:
            ticker = request.args.get('ticker')
            field = request.args.getlist('field')
            field = [elm + ", " for elm in field]
            field[-1] = field[-1].split(",")[0]
            field = "".join(field)
            sql = "SELECT date, {} FROM `{}`".format(field, ticker)
            facs = conn.execute(sql)
            output = []
            if facs:
                for fac in facs:
                    output.append(dict(fac))
        except Exception as e:
            output = "Please enter the correct field. \
                    (e.g. GVI, EPS, MOM, PE, EV_EBITDA, EV_S, FC_P, CROIC, FC_OI, FC_LTD)"
            print(e)
            pass
        return jsonify({"result": output})


class FacByDateFeildApi(Resource):

    def get(self):
        try:
            date = request.args.get('date')
            field = request.args.getlist('field')
            field = [elm + ", " for elm in field]
            field[-1] = field[-1].split(",")[0]
            field = "".join(field)
            ticker_list = conn.table_names()
            sql = ""
            for ticker in ticker_list:
                if ticker != ticker_list[-1]:
                    sql += "SELECT {} FROM `{}` WHERE date = '{}' union all ".format(field, ticker, date)
                else:
                    sql += "SELECT {} FROM `{}` WHERE date = '{}'".format(field, ticker, date)
            facs = conn.execute(sql)
            output = []
            if facs:
                i = 0
                for fac in facs:
                    fac_dict = dict(fac)
                    fac_dict['ticker'] = ticker_list[i]
                    output.append(fac_dict)
                    i += 1
        except Exception as e:
            output = "Please enter the correct date & field. \
                    (e.g. GVI, EPS, MOM, PE, EV_EBITDA, EV_S, FC_P, CROIC, FC_OI, FC_LTD)"
            print(e)
            pass
        return jsonify({"result": output})
