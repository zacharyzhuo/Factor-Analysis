# api usage
<!-- calendar -->
get trade day
http://140.115.87.197:8090/cal?country=TW&date=2010-03-22&how=3&freq=s

payloads = {
    'country': 'TW',
    'date': '2020-03-22',
    'how': 1,
    'freq': 's',
}
response = requests.get(server_ip+"cal", params=payloads)
date = json.loads(response.text)['result']

get all trade day
http://140.115.87.197:8090/cal/get_all_date?country=TW

payloads = {
    'country': 'TW',
}
response = requests.get(server_ip+"cal/get_all_date", params=payloads)
date = json.loads(response.text)['result']

get report day
http://140.115.87.197:8090/cal/get_report_date?country=TW&date=2010-12-25

payloads = {
    'country': 'TW',
    'date': '2020-03-22',
}
response = requests.get(server_ip+"cal/get_report_date", params=payloads)
date = json.loads(response.text)['result']

***

<!-- stock -->
get all ticker
http://140.115.87.197:8090/stk/stk_list

response = requests.get(server_ip+"stk/stk_list", params=payloads)
date = json.loads(response.text)['result']

get stock price of one ticker
http://140.115.87.197:8090/stk/get_ticker_all_stk?ticker_list=1101&ticker_list=1102

payloads = {
    'ticker_list': ['1101', '1102'],
}
response = requests.get(server_ip+"stk/get_ticker_all_stk", params=payloads)
date = json.loads(response.text)['result']

get stock price of one ticker during the selected period
http://140.115.87.197:8090/stk/get_ticker_period_stk?ticker_list=1101&ticker_list=1102&start_date=2000-03-22&end_date=2018-03-22

payloads = {
    'ticker_list': ['1101', '1102'],
    'date': '2020-03-22',
}
response = requests.get(server_ip+"stk/get_ticker_period_stk", params=payloads)
date = json.loads(response.text)['result']

<!-- stock index -->
get all ticker
http://140.115.87.197:8090/stk_idx/stk_idx_list

response = requests.get(server_ip+"stk_idx/stk_idx_list", params=payloads)
date = json.loads(response.text)['result']

get stock price of one ticker
http://140.115.87.197:8090/stk_idx/get_ticker_all_stk_idx?ticker_list=m1100&ticker_list=m1200

payloads = {
    'ticker_list': ['m1100', 'm1200'],
}
response = requests.get(server_ip+"stk_idx/get_ticker_all_stk_idx", params=payloads)
date = json.loads(response.text)['result']

get stock price of one ticker during the selected period
http://140.115.87.197:8090/stk_idx/get_ticker_period_stk_idx?ticker_list=m1100&ticker_list=m1200&date=20000101-20000202

payloads = {
    'ticker_list': ['m1100', 'm1200'],
    'date': '2020-03-22',
}
response = requests.get(server_ip+"stk_idx/get_ticker_period_stk_idx", params=payloads)
date = json.loads(response.text)['result']

<!-- indicator -->
get all ticker
http://140.115.87.197:8090/ind/stk_list

response = requests.get(server_ip+"ind/stk_list", params=payloads)
date = json.loads(response.text)['result']

get all indicator data of one ticker
http://140.115.87.197:8090/ind/get_ticker_all_ind?ticker=1101

payloads = {
    'ticker': '1101',
}
response = requests.get(server_ip+"ind/get_ticker_all_ind", params=payloads)
date = json.loads(response.text)['result']

get selected indicator data of one ticker
http://140.115.87.197:8090/ind/get_ticker_ind?ticker=1101&field=季底普通股市值

payloads = {
    'ticker': '1101',
    'field': ['報酬率(季)', '季底普通股市值']
}
response = requests.get(server_ip+"ind/get_ticker_ind", params=payloads)
date = json.loads(response.text)['result']

get selected indicator data of all ticker at selected date
http://140.115.87.197:8090/ind/get_date_ind?date=2020-09-30&field=季底普通股市值

payloads = {
    'date': '2020-03-22',
    'field': ['報酬率(季)', '季底普通股市值']
}
response = requests.get(server_ip+"ind/get_date_ind", params=payloads)
date = json.loads(response.text)['result']

<!-- factor -->
get all ticker
http://140.115.87.197:8090/fac/stk_list

response = requests.get(server_ip+"fac/stk_list", params=payloads)
date = json.loads(response.text)['result']

get all factor data of one ticker
http://140.115.87.197:8090/fac/get_ticker_all_fac?ticker=1101

payloads = {
    'ticker': '1101',
}
response = requests.get(server_ip+"fac/get_ticker_all_fac", params=payloads)
date = json.loads(response.text)['result']

get selected factor data of one ticker
http://140.115.87.197:8090/fac/get_ticker_fac?ticker=1101&field=GVI&field=PE

payloads = {
    'ticker': '1101',
    'field': ['MOM', 'PE'],
}
response = requests.get(server_ip+"fac/get_ticker_fac", params=payloads)
date = json.loads(response.text)['result']

get selected factor data of all ticker at selected date
http://140.115.87.197:8090/fac/get_date_fac?date=2020-09-30&field=GVI&field=PE

payloads = {
    'date': '2020-03-22',
    'field': ['MOM', 'PE'],
}
response = requests.get(server_ip+"fac/get_date_fac", params=payloads)
date = json.loads(response.text)['result']
