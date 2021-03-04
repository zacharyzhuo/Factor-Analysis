import os
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
from utils.config import Config
from utils.general import General


COLOR = [
    'red', 'orange', 'yellow', 'green',
    'skyblue', 'blue', 'purple', 'black',
    'grey', 'pink', 'lime',  'brown', 
    'greenyellow', 'tan', 'm'
]


class RegressionAnalysis:

    def __init__(self, request):
        self.request = request

        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_portfolio_analysis')
        self._general = General()

        self._run_analysis()

    def _run_analysis(self):
        request = self.request

        for target in request['target_list']:
            for strategy in request['strategy_list']:
                for position in request['position_list']:
                    factor_str_list = []
                    df_list = []
                    for factor in request['factor_list']:
                        if strategy == 'B&H':
                            if len(factor) == 1:
                                strategy_label = 0
                            elif len(factor) == 2:
                                strategy_label = 1
                        else:
                            strategy_label = int(self._cfg.get_value('strategy', strategy))
                        factor_str, df = self._read_file(strategy_label, factor)
                        factor_str_list.append(factor_str)
                        df = df.loc[df['position'] == position]
                        df_list.append(df)
                    self._write_result(target, strategy, position, df_list, factor_str_list)
    
    def _read_file(self, strategy, factor):
        # 將[fac1, fac2] 轉成 fac1&fac2
        factor_str = self._general.factor_to_string(factor)
        path = "{}{}/".format(self._path, factor_str)
        file_name = "{}_{}".format(
            strategy,
            factor_str,
        )
        df = pd.read_csv("{}{}.csv".format(path, file_name))
        
        df['group'] = df['file_name'].apply(lambda x: int(x.split("_")[-2]))
        df['position'] = df['file_name'].apply(lambda x: int(x.split("_")[-1]))

        df = df.drop(columns=['Unnamed: 0', 'file_name'])
        df = df[['group', 'position', 'Net Profit (%)', 'CAGR (%)', 'MDD (%)']]
        return factor_str, df
    
    def _write_result(self, target, strategy, position, df_list, factor_str_list):
        path = self._cfg.get_value('path', 'path_to_regression_analysis')
        path = path + target

        # 如果沒有這個因子的資料夾就新增一個
        if not os.path.exists(path):
            os.makedirs(path)

        fig = plt.figure(figsize=(15, 10))
        for i, df in enumerate(df_list):
            ax = sns.regplot(x=df['group'], y=df[target], color=COLOR[i])
            ax.set(xticks=range(1, len(df['group'])+1, 1))

        file_name = "{}_{}_{}".format(target, strategy, position)

        plt.legend(labels=factor_str_list)
        plt.title(file_name, size=24)
        plt.xlabel('Group', size=18)
        plt.ylabel(target, size=18)

        # plt.show()

        fig = ax.get_figure()
        fig.savefig("{}/{}.png".format(path, file_name))
        plt.clf()
