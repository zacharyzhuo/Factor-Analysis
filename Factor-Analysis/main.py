import time

from modules.calendar import Calendar
from modules.factor import Factor
from modules.mystrategy import MyStrategy
from modules.analysis import Analysis


# factor_list = ['GVI', 'EPS', 'MOM', 'PE', 'EV_EBITDA', 'EV_S', 'FC_P', 'CROIC', 'FC_OI', 'FC_LTD']
# 0: equal_weight; 1: equal_risk(ATR); 2: equal_risk(SD)
weight_setting = [0, 1, 2]                  
n_season = [1, 2]
# group = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# position = [5, 10, 15, 30, 90, 150]
factor_list = ['PE', 'EV_EBITDA', 'EV_S', 'GVI']
group = [1, 2, 3, 4, 5, 6]
position = [5, 10, 15, 30, 90]

start_equity = 10000000
start_date = '2010-01-01'
end_date = '2017-12-31'


# strategy_config = {
#     'factor_list': [factor_list[2]],
#     'weight_setting': weight_setting[0],
#     'n_season': n_season[1],
#     'group': group[0],
#     'position': position[0],
#     'start_equity': start_equity,
#     'start_date': start_date,
#     'end_date': end_date,
# }
# cal = Calendar('TW')
# fac = Factor(strategy_config['factor_list'])

# start = time.time()
# my_stra = MyStrategy(strategy_config, cal, fac)
# end = time.time()
# print("Execution time: %f second" % (end - start))


cal = Calendar('TW')
for factor in factor_list:
    fac = Factor([factor])
    for gro in group:
        for pos in position:
            # try:
            start = time.time()
            strategy_config = {
                'factor_list': [factor],
                'weight_setting': weight_setting[0],
                'n_season': n_season[0],
                'group': gro,
                'position': pos,
                'start_equity': start_equity,
                'start_date': start_date,
                'end_date': end_date,
            }
            my_stra = MyStrategy(strategy_config, cal, fac)
            end = time.time()
            print("Execution time: %f second" % (end - start))
            # except Exception as e:
            #     print(e)
            #     pass  


# analysis = Analysis(start_equity, start_date, end_date)
# analysis.anslysis_portfolio()
# analysis.rank_portfolio_return()
# analysis.plot_net_profit_years()
       