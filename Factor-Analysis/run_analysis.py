from analysis.analysis import Analysis
from utils.general import General


general = General()
analysis = Analysis()

factor_list = [
    # ['FCF_P'], 
    ['EV_EBITDA'],
    # ['P_B'], 
    # ['P_S'], 
    # ['MOM'],
    # ['EPS'], 
    # ['ROIC'], 
    # ['FCF_OI'],
    # ['EV_EBITDA', 'ROIC'],
    # ['P_B', 'EPS'],
    # ['FCF_P', 'MOM'],
    # ['FCF_OI', 'P_S'],
]

# 權益曲線折線圖
def plot_equity_curve():
    request = {
        'factor_list': general.factor_list_to_string(factor_list),
        'strategy_list': [1],
        'window_list': [0],
        'method_list': [5015, 5010, 5005, 5020, 5025],
        # 'group_list': [1, 2, 3, 4, 5], 
        'group_list': [1], 
        'position_list':[6, 15],
        # 'position_list':[15, 60, 150],
    }
    request = {
        'factor_list': general.factor_list_to_string(factor_list),
        'strategy_list': [0],
        'window_list': [0],
        'method_list': [0],
        # 'group_list': [1, 2, 3, 4, 5], 
        'group_list': [5], 
        # 'position_list':[6, 15, 60, 150, 300],
        'position_list':[6],
    }
    analysis.plot_equity_curve(request)

# 權益曲線+資金利用率折線圖
def plot_equity_curve_and_cap_util_rate():
    request = {
        'factor_list': general.factor_list_to_string(factor_list),
        'strategy_list': [1],
        'window_list': [2],
        'method_list': [0, 1],
        'group_list': [5], 
        'position_list':[15],
    }
    analysis.plot_equity_curve_and_cap_util_rate(request)

# 各群組各持有股數熱區圖
def plot_performance_heatmap():
    request = {
        'factor': general.factor_list_to_string(factor_list),
        'strategy': 1,
        'window': 2,
        'method': 0,
        # 'perf_ind': 'CAGR[%]',
        'perf_ind': 'MDD[%]',
        # 'perf_ind': 'MAR',
    }
    analysis.plot_performance_heatmap(request)

# 窗格獲利分布柱狀圖
def plot_window_profit_bar_chart():
    request = {
        'factor_list': general.factor_list_to_string(factor_list),
        'strategy_list': [1],
        'window_list': [1],
        'method_list': [0],
        'group_list': [4], 
        'position_list': [6],
    }
    analysis.plot_window_profit_bar_chart(request)

# 獲利分布柱狀圖
def plot_profit_bar_chart():
    request = {
        'factor_list': general.factor_list_to_string(factor_list),
        'strategy_list': [1],
        'window_list': [2],
        'method_list': [0],
        'group_list': [1], 
        'position_list': [6],
    }
    analysis.plot_profit_bar_chart(request)

# 因子線性回歸圖
def plot_linear_regression():
    request = {
        'factor_list': factor_list,
        'strategy': 1,
        'window': 0,
        'method': 1,
        'position': 300,
        # 'perf_ind': 'CAGR[%]',
        'perf_ind': 'MDD[%]',
    }
    analysis.plot_linear_regression(request)

# 條件查詢績效
def query_performance_file():
    factor_list = [
        # ['FCF_P'], 
        ['EV_EBITDA'],
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

    request = {
        'factor': general.factor_list_to_string(factor_list),
        'strategy': 1,
        'method': 1,
    }

    df = analysis.read_performance_file()

    # df = df.loc[
    #     (df['factor'] == request['factor']) &
    #     (df['strategy'] == request['strategy']) &
    #     (df['method'] == request['method'])
    # ]

    # df = df.sort_values(by=['CAGR[%]'], ascending=False)
    # df = df.sort_values(by=['MDD[%]'], ascending=False)
    df = df.sort_values(by=['MAR'], ascending=False)

    print(df.head(20))

# 輸出所有實驗組合績效
def output_performance_file():
    request = {
        'factor_list': general.factor_list_to_string(factor_list),
        'strategy_list': [0, 1],
        'window_list': [0],
        'method_list': [0, 1],
        'group_list': [1, 2, 3, 4, 5],
        'position_list':[6, 15, 60, 150, 300],
    }
    analysis.output_performance_file(request)

# 輸出所有實驗組合績效
def output_linear_regression_file():
    request = {
        'factor_list': factor_list,
        'strategy_list': [0, 1],
        'window_list': [0],
        'method_list': [0, 1],
        'position_list': [6, 15, 60, 150, 300],
        'perf_ind_list': ['CAGR[%]', 'MDD[%]'],
    }
    request = {
        'factor_list': factor_list,
        'strategy_list': [1],
        'window_list': [1, 2],
        'method_list': [0],
        'position_list': [6, 15, 60, 150, 300],
        'perf_ind_list': ['CAGR[%]', 'MDD[%]'],
    }
    analysis.output_linear_regression_file(request)   

# plot_equity_curve()
# plot_equity_curve_and_cap_util_rate()
# plot_performance_heatmap()
# plot_window_profit_bar_chart()
plot_profit_bar_chart()
# plot_linear_regression()
# query_performance_file()
# output_performance_file()
# output_linear_regression_file()
