import time

from modules.mystrategy import MyStrategy
from modules.analysis import Analysis

# 0: equal_weight; 1: equal_risk(ATR); 2: equal_risk(SD)
weight_setting = [0, 1, 2]                  
factor_list = ['GVI', 'EPS', 'MOM', 'PE', 'EV_EBITDA', 'EV_S', 'FC_P', 'CROIC', 'FC_OI', 'FC_LTD']
group = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
position = [5, 10, 15, 30, 90, 150]
n_season = [1, 2]

start_equity = 10000000
start_date = '2010-01-01'
end_date = '2017-12-31'


# for factor in factor_list:
#     for gro in group:
#         for pos in position:
#             try:
#                 start = time.time()
#                 my_stra = MyStrategy(strategy=strategy[0],
#                                     optimization_setting=optimization_setting[0],
#                                     weight_setting=weight_setting[0],
#                                     factor_list=[factor],
#                                     group=gro,
#                                     position=pos,
#                                     start_equity=start_equity,
#                                     start_date=start_date,
#                                     end_date=end_date)
#                 end = time.time()
#                 print("Execution time: %f second" % (end - start))
#             except Exception as e:
#                 print(e)
#                 pass
        
start = time.time()

strategy_config = {
    'weight_setting': weight_setting[0],
    'factor_list': [factor_list[2]],
    'group': group[0],
    'position': position[0],
    'n_season': n_season[0],
    'start_equity': start_equity,
    'start_date': start_date,
    'end_date': end_date,
}
my_stra = MyStrategy(strategy_config)

end = time.time()
print("Execution time: %f second" % (end - start))
        


# analysis = Analysis(start_equity, start_date, end_date)
        