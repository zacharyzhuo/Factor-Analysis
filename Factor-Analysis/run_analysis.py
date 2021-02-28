from multiprocessing import Process, freeze_support
from analysis.portfolio_analysis import PortfolioAnalysis

# 使用 multiprocessing 必須加上
if __name__ == "__main__":
    freeze_support()

    factor_list = [['ROE', 'P_B']]

    for factor in factor_list:
        request = {
            'factor_list': factor, 
            'strategy_list': [0, 1, 2, 3], 
            'group_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 
            'position_list':[5, 10, 15, 30, 90, 150],
        }
        PortfolioAnalysis().run_portfolio_analysis(request)
