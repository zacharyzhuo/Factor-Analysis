import time
import multiprocessing

from modules.calendar import Calendar
from modules.factor import Factor
from modules.my_asset import MyAsset
from modules.analysis import Analysis

# 0: one factor; 1: two factor; 2: 窗格+bbands 3: 單純bbands
# strategy = [0, 1, 2]
factor_list = ['GVI', 'EPS', 'MOM', 'PE', 'EV_EBITDA', 'EV_S', 'FC_P', 'CROIC', 'FC_OI', 'FC_LTD']
n_season = [0, 1]
# group = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# position = [5, 10, 15, 30, 90, 150]

strategy = [2]
# factor_list = ['EV_EBITDA']
group = [1]
position = [5]

start_equity = 10000000
start_date = '2010-01-01'
end_date = '2017-12-31'


cal = Calendar('TW')

def job(factor):
    try:
        start = time.time()
        print('factor: ', factor)
        fac = Factor([factor])
        get_factor_time = time.time()
        print("Get factor time: %f second" % (get_factor_time - start))
        for stra in strategy:
            for gro in group:
                for pos in position:
                    strategy_config = {
                        'strategy': stra,
                        'factor_list': [factor],
                        'n_season': n_season[0],
                        'group': gro,
                        'position': pos,
                        'start_equity': start_equity,
                        'start_date': start_date,
                        'end_date': end_date,
                    }
                    my_stra = MyAsset(strategy_config, cal, fac)
                    # end = time.time()
                    # print("Execution time: %f second" % (end - start))
    except Exception as e:
        print(e)


# analysis = Analysis(start_equity, start_date, end_date)
# analysis.analysis_factor_performance(strategy[1], factor_list[9])
# analysis.anslysis_portfolio()
# analysis.rank_portfolio_return()
# analysis.plot_net_profit_years()
       

if __name__ == '__main__':
    for factor in factor_list:
        p = multiprocessing.Process(target=job, args=(factor,))
        p.start()