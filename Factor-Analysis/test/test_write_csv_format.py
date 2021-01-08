import pandas as pd
import numpy as np
import datetime
import requests
import json
import csv
import sys
sys.path.append("../")

df = pd.read_csv('../data/result/output.csv')
df = df.drop('Unnamed: 0', axis=1)
print(df)
columns = df.columns
print(columns)
# df = df[['ticker', 'Start', 'End', 'Start Equity', 'Equity Final [$]',
#        'Net Profit', 'Return [%]', 'Return (Ann.) [%]',
#        'Volatility (Ann.) [%]', 'Sharpe Ratio', 'Max. Drawdown [%]',
#        '# Trades', 'Profit Factor', 'Profit', 'Loss']]
df_dict = df.to_dict('records')
print(df_dict)

with open('test.csv', 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    for elm in df_dict:
        print(elm)
        writer.writerow(elm)