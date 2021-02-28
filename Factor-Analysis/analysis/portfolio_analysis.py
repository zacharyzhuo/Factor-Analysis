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

        for key, file_config_list in batch_analysis_dict.items():
            self._analysis_portfolio(key, file_config_list)

    def _read_portfo_perf_file(self, para_list):
        if para_list[1] not in self._strategy_list:
            self._strategy_list.append(para_list[1])

        # 將[fac1, fac2] 轉成 fac1&fac2
        factor_str = self._general.factor_to_string(para_list[0])
        path = "{}{}/".format(self._path, factor_str)
        file_name = "{}_{}_{}_{}_{}".format(
            para_list[1],
            factor_str,
            str(0), 
            str(para_list[2]), 
            str(para_list[3])
        )

        df = pd.read_csv("{}{}.csv".format(path, file_name))
        with open(path+file_name+'.json', 'r') as file:
            data_dict = json.load(file)

        equtiy_dict = {}
        trades_dict = {}
        for ticker, value in data_dict.items():
            equtiy_dict[ticker] = value['equity_curve']['Equity']
            trades_dict[ticker] = value['trades']

        equity_list = []
        for ticker, value in equtiy_dict.items():
            equity_df = pd.DataFrame.from_dict(value, orient='index', columns=[ticker])
            equity_list.append(equity_df)
        # 將投組內的每個標的的每日權益合併 變成整個投組的每日權益變化
        equity_df = pd.concat(equity_list, axis=1)
        equity_df.index.name = 'date'
        equity_df['total_equity'] = equity_df.iloc[:, -5:].sum(axis=1)

        # 計算每個標的在回測期間內每年的賺賠
        year_list = range(int(self._start_date.split('-')[0]), int(self._end_date.split('-')[0]) + 1)
        # 此 df 為整個投組的績效 先把 "年" 列出來當作 columns name
        trades_df = pd.DataFrame(year_list, columns=['year'])
        for ticker, value in trades_dict.items():
            del value['EntryTime']
            # 單一個股的績效
            ticker_trades_df = pd.DataFrame(value)
            ticker_trades_df.columns = [ticker, 'year']
            # 只留年份數字
            ticker_trades_df['year'] = ticker_trades_df['year'].apply(lambda x: x.split('-')[0]).astype(int)
            # 同樣年份的績效加總
            ticker_trades_df = ticker_trades_df.groupby('year').sum()
            # 與投組內所有標的 同年的績效加總
            trades_df = trades_df.merge(ticker_trades_df, on='year', how='outer')

        trades_df['total_net_profit'] = trades_df.iloc[:, -5:].sum(axis=1)
        trades_df = trades_df.set_index('year')

        print("read {}".format(file_name))
        return {
            'file_name': file_name,
            'strategy': para_list[1],
            'df': df,
            'equity_df': equity_df,
            'trades_df': trades_df,
        }

    def _analysis_portfolio(self, key, file_config_list):
        df_list = []

        for file_config in file_config_list:
            df = file_config['df']
            equity_df = file_config['equity_df']
            porfolio_performance_list = []

            # file name
            porfolio_performance_list.append(file_config['file_name'])

            # Net Profit
            final_equity = df['Equity Final [$]'].sum()
            net_profit_rate = (final_equity - self._start_equity) / self._start_equity * 100
            porfolio_performance_list.append(net_profit_rate)

            # CAGR
            start_date_list = self._start_date.split("-")
            end_date_list = self._end_date.split("-")
            if end_date_list[1] == "1" and end_date_list[2] == "1":
                n = int(end_date_list[0]) - int(start_date_list[0])
            else:
                n = int(end_date_list[0]) - int(start_date_list[0]) + 1
            cagr = ((final_equity / self._start_equity) ** (1/n) - 1) * 100
            porfolio_performance_list.append(cagr)

            # MDD
            mdd = df['Max. Drawdown [%]'].min()
            porfolio_performance_list.append(mdd)

            # # Profit Factor
            # total_profit = df['Profit'].sum()
            # total_loss = df['Loss'].sum()
            # profit_factor = total_profit / total_loss * -1
            # porfolio_performance_list.append(profit_factor)

            # # Standar Error
            # standar_error = equity_df['total_equity'].std(axis = 0, skipna = True)
            # porfolio_performance_list.append(standar_error)

            # # Sharp Ratio
            # sharp_ratio = (df['Return [%]'].mean() - (self._risk_free_rate * 100)) / standar_error
            # porfolio_performance_list.append(sharp_ratio)

            # 把除了檔名的值都取到小數點後兩位
            porfolio_performance_list[1:] = [round(x, 2) for x in porfolio_performance_list[1:]]
            df_list.append(porfolio_performance_list)
        
        # column_name = ['file_name', 'Net Profit (%)', 'CAGR (%)', 'MDD (%)', 'Profit Factor', 'Standar Error', 'Sharp Ratio']
        column_name = ['file_name', 'Net Profit (%)', 'CAGR (%)', 'MDD (%)']
        porfolio_performance_df = pd.DataFrame(df_list, columns=column_name)
        self._write_result(key, porfolio_performance_df)

    def _write_result(self, key, df):
        path = self._cfg.get_value('path', 'path_to_portfolio_analysis')
        path = path + self.factor_stirng

        # 如果沒有這個因子的資料夾就新增一個
        if not os.path.exists(path):
            os.makedirs(path)

        file_name = "{}_{}".format(key, self.factor_stirng)
        path = "{}/{}".format(path, file_name)
        df.to_csv(path + '.csv', header=True)
        print('[Analysis]: completed writing porfolio analysis files')

    # def rank_portfolio_return(self):
    #     df = self._df
    #     portfolio_return_df = df.sort_values(ascending=False, by='Return [%]')
    #     portfolio_return_df = portfolio_return_df.reset_index(drop=True)
    #     portfolio_return_df = portfolio_return_df[['ticker', 'Return [%]', '# Trades']]
    #     print(portfolio_return_df)

    # def plot_net_profit_years(self):
    #     equity_df = self._equity_df
    #     trades_df = self._trades_df

    #     equity_df = equity_df.reset_index()
    #     equity_df['year'] = equity_df['date'].apply(lambda x: x.split('-')[0])
    #     year_list = range(int(self._start_date.split('-')[0]), int(self._end_date.split('-')[0])+1)
    #     start_equity_list = []
    #     for year in year_list:
    #         this_year_df = equity_df.loc[equity_df['year'] == str(year)]
    #         start_equity_of_first_day = this_year_df['total_equity'].iloc[0]
    #         start_equity_list.append(start_equity_of_first_day)

    #     trades_df['start_equity'] = start_equity_list
    #     trades_df['net_profit_rate'] = trades_df['total_net_profit']/trades_df['start_equity']*100
        
    #     color_list = []
    #     for i in range(len(trades_df['net_profit_rate'])):
    #         if trades_df['net_profit_rate'].iloc[i] >= 0:
    #             color_list.append('r')
    #         else:
    #             color_list.append('g')
    #     ax = trades_df['net_profit_rate'].plot(kind="bar", color=color_list)
    #     ax.set_xlabel("Year")
    #     ax.set_ylabel("Net Profit (%)")
    #     plt.show()
