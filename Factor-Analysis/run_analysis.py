from multiprocessing import Process, freeze_support
from analysis.portfolio_analysis import PortfolioAnalysis
from analysis.regression_analysis import RegressionAnalysis
from utils.general import General

# 使用 multiprocessing 必須加上
if __name__ == "__main__":
    # freeze_support()

    factor_list = [
        ['FCF_P', 'EPS'], ['MOM_52w_PR', 'P_B'], ['EV_S', 'MOM_7m'], ['FCF_P', 'MOM_7m'],
        ['MOM_52w_PR', 'FCF_P'], ['EV_EBITDA', 'FCF_OI'], ['FCF_P', 'CROIC'], ['FCFPS', 'EV_EBITDA'],
        ['ROIC', 'P_S'], ['ROE', 'P_B'], ['P_B', 'OCF_E'], ['CROIC', 'P_IC'],
        ['P_B', 'EP'], ['FCF_OI', 'P_S'], ['P_B', 'EPS'],
    ]

    # for factor in factor_list:
    #     request = {
    #         'factor_list': factor, 
    #         'strategy_list': [0, 1, 2, 3], 
    #         'group_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 
    #         'position_list':[5, 10, 15, 30, 90, 150],
    #     }
    #     PortfolioAnalysis().run_portfolio_analysis(request)

    request = {
        'factor_list': factor_list, 
        'strategy_list': ['B&H', 'BB+W', 'BB'],
        'position_list':[5, 10, 15, 30, 90, 150],
        'target_list': ['Net Profit (%)', 'CAGR (%)', 'MDD (%)'],
    }
    RegressionAnalysis(request)
