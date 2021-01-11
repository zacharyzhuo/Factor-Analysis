import pandas as pd
import numpy as np
import datetime
import requests
import json
import talib
import sys
sys.path.append("../")


from backtesting import Backtest, Strategy
from strategys.ktn_channel import KTNChannel
from strategys.buy_and_hold import BuyAndHold

from modules.calendar import Calendar
from modules.factor import Factor
from modules.portfolio import Portfolio
from modules.analysis import Analysis


server_ip = "http://140.115.87.197:8090/"

strategy = [0, 1]                           # 0: BuyAndHold; 1: KTNChannel
optimization_setting = [0, 1]               # 0: 無變數(or單一變數); 1: 最佳化變數
weight_setting = [0, 1, 2]                  # 0: equal_weight; 1: equal_risk(ATR); 2: equal_risk(SD)
factor_name = ['GVI', 'EPS', 'MOM', 'PE', 'EV_EBITDA', 'EV_S', 'FC_P', 'CROIC', 'FC_OI', 'FC_LTD']
group = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
position = [5, 10, 15, 30, 90, 150]

start_equity = 2000000
start_date = '2010-01-01'
end_date = '2017-12-31'
risk_free_rate = 0.01

print('start_equity: ', start_equity)

ticker_list = ['8277']
# ticker_list = ['8277', '3450', '1702', '3306', '3533']
# ticker_list = ['8277', '3450', '1702', '3306', '3533', '2425', '1418', '3324', '2428', '6124']

stk_price_dict = {}
ticker_equity_dict = {}
backtest_output_dict = {}

cal = Calendar('TW')

start_date = start_date.split("-")
start_date = "".join(start_date)
end_date = end_date.split("-")
end_date = "".join(end_date)
payloads = {
    'ticker_list': ticker_list,
    'date': start_date + "-" + end_date
}
response = requests.get(server_ip + "stk/get_ticker_period_stk", params=payloads)
output_dict = json.loads(response.text)['result']

for ticker in ticker_list:
    stk_df = pd.DataFrame(output_dict[ticker])
    stk_df['date'] = [datetime.datetime.strptime(elm, "%Y-%m-%d") for elm in stk_df['date']]
    stk_df.set_index("date", inplace=True)
    stk_df.columns = ['Close', 'High', 'Low', 'Open', 'Volume', 'outstanding_share']
    stk_df = stk_df.drop('outstanding_share', axis=1)
    stk_df = stk_df.fillna(0).astype(int)
    output_dict[ticker] = stk_df
stk_price_dict = output_dict
print('stk_price_dict: ', stk_price_dict)


# each_equity = start_equity / len(ticker_list)
# for ticker in ticker_list:
#     ticker_equity_dict[ticker] = each_equity


for ticker in ticker_list:
    BuyAndHold.set_param(BuyAndHold, factor_name[2], ticker, cal)
    bt = Backtest(stk_price_dict[ticker],
                    BuyAndHold,
                    # cash=int(ticker_equity_dict[ticker]),
                    cash=start_equity,
                    commission=0.0005,
                    exclusive_orders=True)
    output = bt.run()
    bt.plot()
    backtest_output_dict[ticker] = output

    trades_df = output['_trades']
    trades_df['year'] = pd.DatetimeIndex(trades_df['ExitTime']).year
    trades_df = trades_df[['PnL', 'year']]
    print(output)
    print(trades_df)

