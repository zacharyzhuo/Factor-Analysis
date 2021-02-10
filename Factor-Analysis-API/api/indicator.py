import json
import pandas as pd
from flask import jsonify
from flask_restful import Resource
from flask_restful import request
from datetime import datetime
from utils.db import ConnMysql


mydb = ConnMysql()
db_name = "indicator"
conn = mydb.connect_db(db_name)


class IndListApi(Resource):

    def get(self):
        table_name_list = conn.table_names()
        return jsonify({"result": table_name_list})


class IndByTickerApi(Resource):

    def get(self):
        output = []
        try:
            ticker = request.args.get('ticker')
            sql = "SELECT * FROM `{}`".format(ticker)
            inds = conn.execute(sql)
            if inds:
                for ind in inds:
                    ind = dict(ind)
                    del ind["index"]
                    output.append(ind)
        except Exception as e:
            output = "No such ticker"
            print(e)
        return jsonify({"result": output})


class IndByTickerFeildApi(Resource):

    def get(self):
        try:
            ticker = request.args.get('ticker')
            field = request.args.getlist('field')
            field = [elm + ", " for elm in field]
            field[-1] = field[-1].split(",")[0]
            field = "".join(field)
            sql = "SELECT date, {} FROM `{}`".format(field, ticker)
            inds = conn.execute(sql)
            output = []
            if inds:
                for ind in inds:
                    output.append(dict(ind))
        except Exception as e:
            output = "Please enter the correct field. \
                    (e.g. 銀行借款－非流動, 報酬率(季), 季底普通股市值, 收盤價(元), \
                    本益比-TSE, 歸屬母公司淨利（損）, 每股淨值(B), 每股盈餘, 淨負債, \
                    營業收入淨額, 稅前息前折舊前淨利, 股東權益總額, 自由現金流量(D), 負債及股東權益總額)"
            print(e)
            pass
        return jsonify({"result": output})


class IndByDateFeildApi(Resource):
    
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
            inds = conn.execute(sql)
            output = []
            if inds:
                i = 0
                for ind in inds:
                    ind_dict = dict(ind)
                    ind_dict['ticker'] = ticker_list[i]
                    output.append(ind_dict)
                    i += 1
        except Exception as e:
            output = "Please enter the correct field. \
                    (e.g. 銀行借款－非流動, 報酬率(季), 季底普通股市值, 收盤價(元), \
                    本益比-TSE, 歸屬母公司淨利（損）, 每股淨值(B), 每股盈餘, 淨負債, \
                    營業收入淨額, 稅前息前折舊前淨利, 股東權益總額, 自由現金流量(D), 負債及股東權益總額)"
            print(e)
            pass
        return jsonify({"result": output})
