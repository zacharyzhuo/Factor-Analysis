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

date = '2017-09-30'
payloads = {
    'date': date,
    'field': ['MOM'],
}
response = requests.get(server_ip+"fac/get_date_fac", params=payloads)
fac_df = json.loads(response.text)['result']
fac_df = pd.DataFrame(fac_df)
print('original')
print(fac_df)
print(response.elapsed)
