import time
from multiprocessing import Process, freeze_support
from utils.config import Config
from service.calendar import Calendar
from service.factor import Factor
from modules.my_asset import MyAsset
from analysis.analysis import Analysis

# 0: one factor; 1: two factor; 2: 窗格+bbands 3: 單純bbands
# strategy = [0, 1, 2]
factor_list = ['GVI', 'EPS', 'MOM', 'PE', 'EV_EBITDA', 'EV_S', 'FC_P', 'CROIC', 'FC_OI', 'FC_LTD']
n_season = [0, 1]
group = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
position = [5, 10, 15, 30, 90, 150]

# ----------------------------------------------------------

strategy = [1]
factor_list = ['PE', 'FC_LTD']
group = [1]
position = [5]

# 使用 multiprocessing 必須加上
if __name__ == "__main__":
    freeze_support()
    cfg = Config()
    
    try:
        cal = Calendar('TW')
        get_factor_start = time.time()
        fac = Factor(factor_list)
        get_factor_end = time.time()
        print("Get factor time: %f second" % (get_factor_end - get_factor_start))
        for factor in factor_list:
            for stra in strategy:
                for gro in group:
                    for pos in position:
                        start = time.time()
                        strategy_config = {
                            'strategy': stra,
                            'factor_list': [factor, 'FC_LTD'],
                            'n_season': n_season[0],
                            'group': gro,
                            'position': pos,
                            'start_equity': int(cfg.get_value('parameter', 'start_equity')),
                            'start_date': cfg.get_value('parameter', 'start_date'),
                            'end_date': cfg.get_value('parameter', 'end_date'),
                        }
                        my_stra = MyAsset(strategy_config, cal, fac)
                        end = time.time()
                        print("Execution time: %f second" % (end - start))
            break
    except Exception as e:
        print(e)


    # analysis = Analysis(start_equity, start_date, end_date)
    # analysis.analysis_factor_performance(0, factor_list[0])

    # porfolio_performance_list = analysis.anslysis_portfolio()
    # print(porfolio_performance_list)
    # analysis.rank_portfolio_return()
    # analysis.plot_net_profit_years()

    # cal = Calendar('TW')
    # get_factor_start = time.time()
    # fac = Factor(factor_list)
    # factor_all_date_df = fac.factor_df_dict['GVI']
    # factor_df = factor_all_date_df.loc['2020-09-30'].to_frame()
    # group_list = fac.rank_factor(factor_df, 'GVI')
    # get_factor_end = time.time()
    # print("Get factor time: %f second" % (get_factor_end - get_factor_start))
       