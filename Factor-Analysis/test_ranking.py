import pandas as pd
import numpy as np
import datetime
import requests
import json
import talib
import ta

from modules.factor import Factor
from modules.calendar import Calendar
from modules.plot import Plot
from strategys.ktnchannel import KTNChannel
from strategys.buyandhold import BuyAndHold
from strategys.double_moving_average import DoubleMA



date = '2017-09-30'
# factor_name = ['GVI', 'EPS', 'MOM', 'PE', 'EV_EBITDA', 'EV_S', 'FC_P', 'CROIC', 'FC_OI', 'FC_LTD']
factor_name = ['PE', 'EV_EBITDA', 'EV_S', 'FC_LTD']
group = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

cal = Calendar('TW')
date = cal.advance_date(date, 0, 's')
target_rank_df = pd.read_csv('rank.csv')
target_rank_df = target_rank_df[target_rank_df['time'] == 2017930]

print('------------------')
for fac in factor_name:
    factor = Factor(fac, date)
    ranking_list = factor.rank_factor()
    # fac_target_rank_df = target_rank_df[['stock', fac+'_rank']]
    print('this is factor: ', fac)
    for elm in group:
        print('this is group ', elm)
        ticker_group_df = ranking_list[elm - 1]
        ticker_group_df = ticker_group_df[['ticker', fac]]
        temp_target_rank_df = target_rank_df[target_rank_df[fac+'_rank'] == elm]
        result_target_rank_df = temp_target_rank_df[['stock', fac]]
        # print(ticker_group_df)
        # print(result_target_rank_df)

        result_list = []
        target_rank_list = result_target_rank_df['stock'].astype(str).tolist()
        ticker_group_list = ticker_group_df['ticker'].tolist()

        for elm in ticker_group_df['ticker']:
            if elm in target_rank_list:
                result_list.append(elm)
        print('len: ', len(result_list))
    print('------------------')
