import pandas as pd
import numpy as np
import datetime
import requests
import json
import talib
import sys
sys.path.append("../")
from utils.plot import Plot
from service.calendar import Calendar


server_ip = "http://140.115.87.197:8090/"
cal = Calendar('TW')

payloads = {
    'ticker_list': ['1524'],
    'start_date': cal.get_trade_date('2010-01-01', (1+30)*-1, 'd'),
    'end_date': cal.get_trade_date('2010-03-31', 1, 'd'),
}
response = requests.get(server_ip+"stk/get_ticker_period_stk", params=payloads)
stk_dict = json.loads(response.text)['result']

stk_df = pd.DataFrame(stk_dict[ticker_list[0]])
stk_df['date'] = [datetime.datetime.strptime(elm, "%Y-%m-%d") for elm in stk_df['date']]
stk_df.set_index("date", inplace=True)
stk_df.columns = ['Close', 'High', 'Low', 'Open', 'Volume', 'outstanding_share']
stk_df = stk_df.drop('outstanding_share', axis=1)
stk_df = stk_df.dropna()
print(stk_df)

up_band, mid, down_band = BBANDS(
    stk_df['Close'], timeperiod=30,
    nbdevup=1.5, nbdevdn=1.5,
    matype=0
)

plot = Plot()
plot.plot_candlestick(df=stk_df, addplot_list=[up_band, mid, down_band])
