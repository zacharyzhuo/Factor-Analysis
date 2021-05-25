from multiprocessing import Process, freeze_support
from analysis.regression_analysis import RegressionAnalysis
from analysis.analysis import Analysis
from utils.general import General


# 使用 multiprocessing 必須加上
if __name__ == "__main__":
    general = General()
    analysis = Analysis()
    # freeze_support()

    factor_list = [
        ['EV_EBITDA', 'ROIC'], ['P_B', 'EPS'], ['FCF_P', 'MOM'],
        ['FCF_OI', 'P_S'], ['FCF_P'], ['EV_EBITDA'],
        ['P_B'], ['P_S'], ['MOM'],
        ['EPS'], ['ROIC'], ['FCF_OI']
    ]

    factor_list = [
        ['FCF_P'], 
        # ['EV_EBITDA'],
        # ['P_B'], 
        # ['P_S'], 
        # ['MOM'],
        # ['EPS'], 
        # ['ROIC'], 
        # ['FCF_OI']
        # ['EV_EBITDA', 'ROIC'],
        # ['P_B', 'EPS'],
        # ['FCF_P', 'MOM'],
        # ['FCF_OI', 'P_S'],
    ]

    # 權益曲線折線圖
    # ======================================================

    request = {
        'factor_list': general.factor_list_to_string(factor_list),
        'strategy_list': [1],
        'window_list': [0],
        'method_list': [0],
        # 'group_list': [1, 2, 3, 4, 5], 
        'group_list': [2], 
        'position_list':[6, 15, 60, 150, 300],
        # 'position_list':[6, 15],
    }
    analysis.plot_equity_curve(request)
    
    # 資金利用率折線圖
    # ======================================================

    request = {
        'factor_list': general.factor_list_to_string(factor_list),
        'strategy_list': [1],
        'window_list': [0],
        'method_list': [0, 1],
        'group_list': [1], 
        'position_list':[300],
    }
    # analysis.check_cap_util_rate(request)

    # 各群組各持有股數熱區圖
    # ======================================================

    request = {
        'factor': general.factor_list_to_string(factor_list),
        'strategy': 1,
        'method': 0,
        'perf_ind': 'CAGR[%]',
        # 'perf_ind': 'MDD[%]',
        # 'perf_ind': 'MAR',
    }
    # analysis.plot_performance_heatmap(request)

    # 獲利分布柱狀圖
    # ======================================================

    request = {
        'factor': general.factor_list_to_string(factor_list),
        'strategy': 0,
        'window': 0,
        'method': 0,
        'group': 1, 
        'position': 6,
    }
    # analysis.plot_profit_bar_chart(request)

    # 因子線性回歸圖
    # ======================================================

    factor_list = [
        ['EV_EBITDA', 'ROIC'], ['P_B', 'EPS'], ['FCF_P', 'MOM'],
        ['FCF_OI', 'P_S'], ['FCF_P'], ['EV_EBITDA'],
        ['P_B'], ['P_S'], ['MOM'],
        ['EPS'], ['ROIC'], ['FCF_OI']
    ]

    request = {
        'factor_list': factor_list,
        'strategy': 0,
        'window': 0,
        'method': 0,
        'position': 300,
        'perf_ind': 'CAGR[%]',
        # 'perf_ind': 'MDD[%]',
        # 'perf_ind': 'MAR',
    }
    # analysis.plot_linear_regression(request)

    # 條件查詢績效
    # ======================================================

    request = {
        'factor': general.factor_list_to_string(factor_list),
        'strategy': 1,
        'method': 0,
    }
    
    # df = analysis.query_performance_file()

    # df = df.loc[
    #     (df['factor'] == request['factor']) &
    #     (df['strategy'] == request['strategy']) &
    #     (df['method'] == request['method'])
    # ]
    
    # print(df)

    # 輸出所有實驗組合績效
    # ======================================================

    request = {
        'factor_list': general.factor_list_to_string(factor_list),
        'strategy_list': [0, 1],
        'window_list': [0],
        'method_list': [0, 1],
        'group_list': [1, 2, 3, 4, 5],
        'position_list':[6, 15, 60, 150, 300],
    }
    # analysis.output_performance_file(request)



    # request = {
    #     'factor_list': factor_list, 
    #     'strategy_list': ['B&H', 'BB+W', 'BB'],
    #     'position_list':[5, 10, 15, 30, 90, 150],
    #     'target_list': ['Net Profit (%)', 'CAGR (%)', 'MDD (%)'],
    # }
    # RegressionAnalysis(request)
    
    # ======================================================
    
