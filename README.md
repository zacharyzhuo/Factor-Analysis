// 虛擬環境

.\Factor-Analysis\venv\Scripts\activate
deactivate

python -m venv venv
pip freeze > requirements.txt
python -m pip install -r requirements.txt

# api usage
<!-- calendar -->
get trade day
http://140.115.87.197:8090/cal?country=TW&date=2010-03-22&how=3&freq=m

get all trade day
http://140.115.87.197:8090/cal/get_all_date?country=TW


<!-- stock -->
get all ticker
http://140.115.87.197:8090/stk/stk_list

get stock price of one ticker
http://140.115.87.197:8090/stk/get_ticker_all_stk?ticker_list=1101&ticker_list=1102

get stock price of one ticker during the selected period
http://140.115.87.197:8090/stk/get_ticker_period_stk?ticker_list=1101&ticker_list=1102&date=20000101-20000202


<!-- stock index -->
get all ticker
http://140.115.87.197:8090/stk_idx/stk_idx_list

get stock price of one ticker
http://140.115.87.197:8090/stk_idx/get_ticker_all_stk_idx?ticker_list=m1100&ticker_list=m1200

get stock price of one ticker during the selected period
http://140.115.87.197:8090/stk_idx/get_ticker_period_stk_idx?ticker_list=m1100&ticker_list=m1200&date=20000101-20000202


<!-- indicator -->
get all ticker
http://140.115.87.197:8090/ind/stk_list

get all indicator data of one ticker
http://140.115.87.197:8090/ind/get_ticker_all_ind?ticker=1101

get selected indicator data of one ticker
http://140.115.87.197:8090/ind/get_ticker_ind?ticker=1101&field=報酬率％_月&field=季底普通股市值

get selected indicator data of all ticker at selected date
http://140.115.87.197:8090/ind/get_date_ind?date=2020-09-30&field=報酬率％_月&field=季底普通股市值


<!-- factor -->
get all ticker
http://140.115.87.197:8090/fac/stk_list

get all factor data of one ticker
http://140.115.87.197:8090/fac/get_ticker_all_fac?ticker=1101

get selected factor data of one ticker
http://140.115.87.197:8090/fac/get_ticker_fac?ticker=1101&field=GVI&field=MOM&field=PE

get selected factor data of all ticker at selected date
http://140.115.87.197:8090/fac/get_date_fac?date=2020-09-30&field=GVI&field=MOM&field=PE


<!-- call api by another way-->
server_ip = "http://140.115.87.197:8090/"
payloads = {
    'country': 'TW',
    'date': '2017-12-31',
    'how': 1,
    'freq': 's',
}
response = requests.get(server_ip+"cal", params=payloads)
date = json.loads(response.text)['result']
print('date: ', date)
