import os
import pandas as pd
import json
import matplotlib.pyplot as plt
from multiprocessing.dummy import Pool as ThreadPool
import pathos
from multiprocessing import Pool
from utils.config import Config
from utils.general import General


class PortfolioAnalysis:

    def __init__(self):
        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_portfolio_performance')
        self._risk_free_rate = float(self._cfg.get_value('parameter', 'risk_free_rate'))
        self._start_equity = int(self._cfg.get_value('parameter', 'start_equity'))
        self._start_date = self._cfg.get_value('parameter', 'start_date')
        self._end_date = self._cfg.get_value('parameter', 'end_date')

        self._general = General()

        # 執行完 _read_portfo_perf_file 會抓出目前的 request 有哪些不重複策略
        self._strategy_list = []
        self.factor_stirng = ""

    def run_portfolio_analysis(self, request):
        self.factor_stirng = self._general.factor_to_string(request['factor_list'])
        print(self.factor_stirng)

        # 將 request 轉換成各種排列組合
        combi_list = self._general.combinate_parameter(
            [request['factor_list']], request['strategy_list'], request['group_list'], request['position_list']
        )

        # 要用幾個執行緒需自己測試
        thread_pool = ThreadPool(10)
        # pool用法: (放需要平行運算的任務, 參數(需要作幾次))
        results = thread_pool.map(self._read_portfo_perf_file, combi_list)
        thread_pool.close()
        thread_pool.join()

        # 預先建立一個字典並以 self._strategy_list 中的策略為 key
        # e.g. batch_analysis_dict[0] = []
        batch_analysis_dict = {}
        for i in self._strategy_list:
            batch_analysis_dict[i] = []

        # 將同樣的策略績效分群
        for result in results:
            batch_analysis_dict[result['strategy']].append(result)

        for strategy, file_config_list in batch_analysis_dict.items():
            self._analysis_portfolio(strategy, file_config_list)

    def _read_portfo_perf_file(self, para_list):
        if para_list[1] not in self._strategy_list:
            self._strategy_list.append(para_list[1])

        # 將[fac1, fac2] 轉成 fac1&fac2
        factor_str = self._general.factor_to_string(para_list[0])
        path = "{}{}/".format(self._path, factor_str)
        file_name = "{}_{}_{}_{}_{}".format(
            factor_str,
            para_list[1],
            str(0), 
            str(para_list[2]), 
            str(para_list[3])
        )

        # performance_df = pd.read_csv("{}{}.csv".format(path, file_name)).drop('Unnamed: 0', axis=1)

        with open(path+file_name+'.json', 'r') as file:
            json_data = json.load(file)
        equity_df = pd.DataFrame.from_dict(json_data)
        equity_df['date']= pd.to_datetime(equity_df['date'])
        equity_df = equity_df.set_index('date')

        print("read {}".format(file_name))
        return {
            'file_name': file_name,
            'strategy': para_list[1],
            # 'performance_df': performance_df,
            'equity_df': equity_df,
        }

    def _analysis_portfolio(self, strategy, file_config_list):
        rows = []

        for file_config in file_config_list:
            equity_df = file_config['equity_df']
            porfolio_performance_list = []

            # [file name]
            porfolio_performance_list.append(file_config['file_name'])

            # [Net Profit]
            final_equity = equity_df['portfolio_equity'].iloc[-1]
            net_profit_rate = (final_equity - self._start_equity) / self._start_equity * 100
            porfolio_performance_list.append(net_profit_rate)

            # [CAGR]
            start_date_list = self._start_date.split("-")
            end_date_list = self._end_date.split("-")
            if end_date_list[1] == "1" and end_date_list[2] == "1":
                n = int(end_date_list[0]) - int(start_date_list[0])
            else:
                n = int(end_date_list[0]) - int(start_date_list[0]) + 1
            cagr = ((final_equity / self._start_equity) ** (1/n) - 1) * 100
            porfolio_performance_list.append(cagr)

            # [MDD]
            highest_equity = equity_df['portfolio_equity'].max()
            MDD = 0
            for i, elm in enumerate(equity_df['portfolio_equity'].values.tolist()):
                drawdown = elm - equity_df['portfolio_equity'].iloc[:i].max()
                if drawdown < MDD:
                    MDD = drawdown
            MDD = MDD / highest_equity *100
            porfolio_performance_list.append(MDD)

            # 把除了檔名的值都取到小數點後兩位
            # porfolio_performance_list[1:] = [round(x, 2) for x in porfolio_performance_list[1:]]
            rows.append(porfolio_performance_list)
        
        column_name = ['file_name', 'Net Profit (%)', 'CAGR (%)', 'MDD (%)']
        porfolio_performance_df = pd.DataFrame(rows, columns=column_name)
        self._write_result(strategy, porfolio_performance_df)

    def _write_result(self, strategy, df):
        path = self._cfg.get_value('path', 'path_to_portfolio_analysis')
        path = path + self.factor_stirng

        # 如果沒有這個因子的資料夾就新增一個
        if not os.path.exists(path):
            os.makedirs(path)

        file_name = "{}_{}".format(strategy, self.factor_stirng)
        path = "{}/{}".format(path, file_name)
        df.to_csv(path + '.csv', header=True)
        print('[Analysis]: completed writing porfolio analysis files')
