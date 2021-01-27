import pandas as pd
import numpy as np
import datetime
import requests
import json
import talib
import sys
sys.path.append("../")
from modules.plot import Plot


server_ip = "http://140.115.87.197:8090/"

ticker_list = ['3550', '3441']
payloads = {
    'ticker_list': [ticker_list[0]],
}
response = requests.get(server_ip+"stk/get_ticker_all_stk", params=payloads)
stk_dict = json.loads(response.text)['result']

stk_df = pd.DataFrame(stk_dict[ticker_list[0]])
stk_df['date'] = [datetime.datetime.strptime(elm, "%Y-%m-%d") for elm in stk_df['date']]
stk_df.set_index("date", inplace=True)
stk_df.columns = ['Close', 'High', 'Low', 'Open', 'Volume', 'outstanding_share']
stk_df = stk_df.drop('outstanding_share', axis=1)
# stk_df = stk_df.interpolate(method='linear', limit_direction='forward', axis=0)
stk_df = stk_df.dropna()
print(stk_df)

plot = Plot()
plot.plot_candlestick(df=stk_df)
