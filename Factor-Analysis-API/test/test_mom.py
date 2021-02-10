import pandas as pd
import numpy as np
import datetime
import math
import datetime
import requests
import json
import sys
sys.path.append("../")


server_ip = "http://140.115.87.197:8090/"
ticker = "1104"
date = '2017-09-30'

payloads = {
    'country': 'TW',
    'date': date,
}
response = requests.get(server_ip+"cal/get_report_date", params=payloads)
report_date = json.loads(response.text)['result']
print('report_date: ', report_date)

report_date = "".join(report_date.split('-'))
payloads = {
    'ticker_list': [ticker],
    'date': report_date+'-'+report_date,
}
response = requests.get(server_ip+"stk/get_ticker_period_stk", params=payloads)
report_stk = json.loads(response.text)['result'][ticker][0]['close']
print('report_stk: ', report_stk)


payloads = {
    'country': 'TW',
    'date': date,
    'how': 1,
    'freq': 's',
}
response = requests.get(server_ip+"cal", params=payloads)
pre_season_date = json.loads(response.text)['result']
print('pre_season_date: ', pre_season_date)

pre_season_date = "".join(pre_season_date.split('-'))
payloads = {
    'ticker_list': [ticker],
    'date': pre_season_date+'-'+pre_season_date,
}
response = requests.get(server_ip+"stk/get_ticker_period_stk", params=payloads)
pre_season_stk = json.loads(response.text)['result'][ticker][0]['close']
print('pre_season_stk: ', pre_season_stk)

return_rate = (report_stk-pre_season_stk)/pre_season_stk*100
print('return_rate: ', return_rate)

