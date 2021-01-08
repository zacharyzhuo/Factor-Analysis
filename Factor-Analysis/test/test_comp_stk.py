import pandas as pd
import numpy as np
import math
import datetime
import requests
import json
import talib
import os
import sys
sys.path.append("../")

print(os.getcwd())

server_ip = "http://140.115.87.197:8090/"


def trans_stk_price(value):
    if value < 10:
        value = math.ceil(value * 100) / 100.0
    elif value > 10 and value < 50:
        value = math.ceil(value * 100) / 100.0
        value_list = str(value).split('.')
        if len(value_list[1]) == 1:
            value_list[1] = value_list[1][0] + '0'
        if (int(value_list[0][1]) == 9 and int(value_list[1][0]) == 9 and int(value_list[1][1]) > 5) or (int(value_list[1][0]) == 9 and int(value_list[1][1]) > 5):
            value_list[0] = str(int(value_list[0]) + 1)
            value_list[1] = '00'
        else:
            if int(value_list[1][1]) < 5 and int(value_list[1][1]) != 0:
                value_list[1] = value_list[1][0] + '5'
            elif int(value_list[1][1]) > 5:
                value_list[1] = str(int(value_list[1][0]) + 1) + '0'
        value_list = ".".join(value_list)
        value = float(value_list)
    elif value > 50 and value < 100:
        value = math.ceil(value * 10) / 10.0
    elif value > 100 and value < 500:
        value = math.ceil(value * 10) / 10.0
        value_list = str(value).split('.')
        if int(value_list[1][0]) < 5 and int(value_list[1][0]) != 0:
            value_list[1] = '5'
        elif int(value_list[1][0]) > 5:
            value_list[0] = str(int(value_list[0]) + 1)
            value_list[1] = '00'
        value_list = ".".join(value_list)
        value = float(value_list)
    elif value > 500 and value < 1000:
        value = math.ceil(value * 1) / 1.0
    elif value > 1000:
        value = math.ceil(value)
        value_list = str(value)
        if int(value_list[3]) < 5 and int(value_list[3]) != 0:
            value_list = value_list[:-1] + '5'
        elif int(value_list[3]) > 5:
            num = value_list[:3]
            num = str(int(num) + 1)
            value_list = num + '0'
        value_list = "".join(value_list)
        value = float(value_list)
    return value


# df = pd.read_excel("./test/data/2010.xlsx")
# df['證券代碼'] = df['證券代碼'].apply(lambda x: x.split(" ")[0])
# df = df[df['證券代碼'] == '1101']
# df.columns = ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']
# df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
# print(df)

ticker_list = ['1101']
payloads = {
    'ticker_list': ticker_list,
    'date': '20100101-20101231',
    # 'date': '20170101-20171231',
}
response = requests.get(server_ip+"stk/get_ticker_period_stk", params=payloads)
stk = json.loads(response.text)['result']
stk = stk[ticker_list[0]]
stk_df = pd.DataFrame(stk)
stk_df = stk_df[['date', 'open', 'high', 'low', 'close', 'volume']]
print(stk_df)
stk_df['open'] = stk_df['open'].apply(lambda x: trans_stk_price(x))
stk_df['high'] = stk_df['high'].apply(lambda x: trans_stk_price(x))
stk_df['low'] = stk_df['low'].apply(lambda x: trans_stk_price(x))
stk_df['close'] = stk_df['close'].apply(lambda x: trans_stk_price(x))
print(stk_df)




# num = 12.8399999
# num = 10.8399999
# num = 59.99999
# num = 109.66
# num = 520.66
# num = 1094.3123
# num = 15.3123
# num = 15.2975

# x = trans_stk_price(num)
# print(x)
