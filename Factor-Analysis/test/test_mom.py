import pandas as pd
import numpy as np
import datetime
import requests
import json
import talib
import sys
sys.path.append("../")

from modules.factor import Factor
from modules.calendar import Calendar

server_ip = "http://140.115.87.197:8090/"

ticker_list = ['1101']
year = ['2010']
this_date = ['03-31', '06-30', '09-30', '12-31']
# this_date = ['05-15', '08-14', '11-14', '03-31']
pre_date = ['12-31', '03-31', '06-30', '09-30']
target_date = ['03-31', '06-30', '09-30', '12-31']

cal = Calendar('TW')

print('-----------------------')
for i in range(4):
    # if this_date[i] == this_date[3]:
    #     this_year = str(int(year[0])+1)
    #     t_date = this_year + "-" + this_date[i]
    # else:
    #     t_date = year[0] + "-" + this_date[i]
    t_date = year[0] + "-" + this_date[i]
    t_date = cal.advance_date(t_date, 0, 'd')
    t_date = "".join(t_date.split('-'))
    print('this date: ', t_date)
    payloads = {
        'ticker_list': ticker_list,
        'date': t_date+"-"+t_date,
    }
    response = requests.get(server_ip+"stk/get_ticker_period_stk", params=payloads)
    t_stk = json.loads(response.text)['result']
    t_stk = t_stk[ticker_list[0]][0]['close']
    print('this stk: ', t_stk)
    if this_date[i] == this_date[0]:
        pre_year = str(int(year[0])-1)
        p_date = pre_year + "-" + pre_date[i]
    else:
        p_date = year[0] + "-" + pre_date[i]
    p_date = cal.advance_date(p_date, 0, 'd')
    p_date = "".join(p_date.split('-'))
    print('pre date: ', p_date)
    payloads = {
        'ticker_list': ticker_list,
        'date': p_date+"-"+p_date,
    }
    response = requests.get(server_ip+"stk/get_ticker_period_stk", params=payloads)
    p_stk = json.loads(response.text)['result']
    p_stk = p_stk[ticker_list[0]][0]['close']
    print('pre stk: ', p_stk)
    mom = (t_stk - p_stk) / p_stk * 100
    print('target date: ', year[0]+'-'+target_date[i])
    print('mom: ', mom)
    # return_rate = (t_stk / p_stk - 1)
    print('-----------------------')




