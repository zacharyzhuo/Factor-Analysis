import numpy as np
from multiprocessing import Process, freeze_support
from analysis.portfolio_analysis import PortfolioAnalysis
from analysis.regression_analysis import RegressionAnalysis
from analysis.analysis import Analysis
from utils.general import General

# 使用 multiprocessing 必須加上
if __name__ == "__main__":
    # freeze_support()

    factor_list = [
        ['FCF_P', 'CROIC'], ['EV_EBITDA', 'ROIC'], ['P_B', 'EP'], ['ROE', 'P_B'],
        ['ROIC', 'P_S'], ['CROIC', 'P_IC'], ['FCFPS', 'EV_EBITDA'], ['FCF_P', 'EPS'],
        ['P_B', 'EPS'], ['FCF_P', 'MOM_7m'], ['EV_S', 'MOM_7m'], ['MOM_52w_PR', 'FCF_P'],
        ['MOM_52w_PR', 'P_B'], ['EV_EBITDA', 'FCF_OI'], ['FCF_OI', 'P_S'], ['P_B', 'OCF_E']
    ]

    factor_list = [
        ['EV_EBITDA', 'ROIC'], ['P_B', 'EPS'], ['FCF_P', 'MOM_7m'],
        ['FCF_OI', 'P_S'], ['FCF_P'], ['EV_EBITDA'],
        ['P_B'], ['P_S'], ['MOM_7m'],
        ['EPS'], ['ROIC'], ['FCF_OI']
    ]

    factor_list = [
        ['EV_EBITDA', 'ROIC'],
        # ['P_B', 'EPS'],
        # ['FCF_P', 'MOM'],
        # ['FCF_OI', 'P_S'],
        # ['FCF_P'], 
        # ['EV_EBITDA'],
        # ['P_B'], 
        # ['P_S'], 
        # ['MOM'],
        # ['EPS'], 
        # ['ROIC'], 
        # ['FCF_OI']
    ]

    request = {
        'factor_list': factor_list,
        'strategy_list': [1],
        'window_list': [0],
        'method_list': [0],
        # 'group_list': [1, 2, 3, 4, 5], 
        'group_list': [1], 
        'position_list':[6, 15, 60, 150, 300],
        # 'position_list':[6, 15],
    }
    # Analysis().plot_equity_curve(request)

    request = {
        'factor_list': factor_list,
        'strategy_list': [1],
        'window_list': [0],
        'method_list': [0, 1],
        'group_list': [1], 
        'position_list':[5],
    }
    Analysis().check_cap_util_rate(request)

    # ======================================================

    # for factor in factor_list:
    #     request = {
    #         'factor_list': factor, 
    #         'strategy_list': [0],
    #         # 'strategy_list': [0, 1, 2],
    #         'group_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 
    #         'position_list':[5, 10, 15, 30, 90, 150],
    #     }
    #     PortfolioAnalysis().run_portfolio_analysis(request)

    # request = {
    #     'factor_list': factor_list, 
    #     'strategy_list': ['B&H', 'BB+W', 'BB'],
    #     'position_list':[5, 10, 15, 30, 90, 150],
    #     'target_list': ['Net Profit (%)', 'CAGR (%)', 'MDD (%)'],
    # }
    # RegressionAnalysis(request)
    
