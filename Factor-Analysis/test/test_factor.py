import pandas as pd
import numpy as np
import datetime
import requests
import json
import talib
import sys
sys.path.append("../")

from api.factor import Factor


factor_list = ['MOM', 'GVI']
fac = Factor(factor_list)
factor_df = fac.factor_df_dict['MOM']
df_list = fac.rank_factor(factor_df, 'MOM', '2002-12-31')
# print(df_list)
# nan_pct = fac.check_nan('MOM', '2002-12-31')
# print(nan_pct)
