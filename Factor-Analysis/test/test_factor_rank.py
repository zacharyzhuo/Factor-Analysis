import pandas as pd
import numpy as np
import datetime
import math
import datetime
import requests
import json
import sys
sys.path.append("../")

from modules.factor import Factor
from modules.calendar import Calendar


server_ip = "http://140.115.87.197:8090/"

fac = 'MOM'
date = '2017-09-30'

factor = Factor(fac, date)
ranking_list = factor.rank_factor()
print(ranking_list)