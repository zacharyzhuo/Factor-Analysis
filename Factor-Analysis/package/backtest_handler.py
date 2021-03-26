import pandas as pd
import numpy as np
import datetime
import requests
import json
import pathos
from multiprocessing import Pool
from backtesting import Backtest, Strategy
from utils.config import Config
from strategy.buy_and_hold import BuyAndHold
from strategy.bbands import BBands


class BacktestHandler:

    def __init__(self, window_config, t2_period, group_ticker, cal):
        self.window_config = window_config
        self._t2_period = t2_period
        # 該群排序完的標的
        self._group_ticker = group_ticker
        self._cal = cal

        self._cfg = Config()
        self._ma_len = 30
        self._band_width = 1.5

        # 選中的標的 B&H: 前幾支標的; BB: 因子排序順序高且先突破的標的
        self.chosen_ticker = []
        self.equity_table = pd.DataFrame()

        trade_dict = self._create_equity_table()
        cash_flow_detail = self._allocate_cash_flow(trade_dict)
        self._allocate_weight(cash_flow_detail)

        # print(self.equity_table)
        # print(cash_flow_detail)


    def _get_stk_price(self):
        api_server_IP = self._cfg.get_value('IP', 'api_server_IP')

        # 單因子 & 雙因子策略
        if self.window_config['strategy'] == 0 or self.window_config['strategy'] == 1:
            # 因為 backtesting 不能在第一天跟最後一天交易 所以必須往前後多加一天
            start_date = self._cal.get_trade_date(self._t2_period[0], -2, 'd')

        # 布林通道策略
        elif self.window_config['strategy'] == 2:
            # 因為要算均線所以要往前多抓幾天
            start_date = self._cal.get_trade_date(self._t2_period[0], (1+self._ma_len)*-1, 'd')

        payloads = {
            'ticker_list': self._group_ticker,
            'start_date': start_date,
            # 其實end date也要多抓一天 才能指定那天出場 但是backtest也會在回測結束時強制全部出場
            'end_date': self._cal.get_trade_date(self._t2_period[1], 1, 'd'),
        }
        response = requests.get("http://{}/stk/get_ticker_period_stk".format(api_server_IP), params=payloads)
        stk_price_dict = json.loads(response.text)['result']

        for ticker in self._group_ticker:
            try:

                stk_df = pd.DataFrame(stk_price_dict[ticker]).drop(['index', 'outstanding_share'], axis=1)
                stk_df['date'] = [datetime.datetime.strptime(elm, "%Y-%m-%d") for elm in stk_df['date']]
                stk_df.set_index("date", inplace=True)
                # 資料庫抓出來會按照字母排序
                stk_df.columns = ['Close', 'High', 'Low', 'Open', 'Volume']
                stk_df = stk_df.dropna()
                stk_price_dict[ticker] = stk_df

            except Exception as e:
                pass

        return stk_price_dict

    def _run_backtest(self, stk_price_dict):
        commission = float(self._cfg.get_value('parameter', 'commission'))
        strat_date = datetime.datetime.strptime(self._t2_period[0], "%Y-%m-%d")
        end_date = datetime.datetime.strptime(self._t2_period[1], "%Y-%m-%d")

        # 使用 inner function 特別獨立出需要多核運算的部分
        def multiprocessing_job(ticker):
            try:
                # 單因子 & 雙因子策略
                if self.window_config['strategy'] == 0 or self.window_config['strategy'] == 1:
                    # 傳入窗格開始與結束時間 即買點與賣點
                    BuyAndHold.set_param(BuyAndHold, [self._t2_period[0]],  [self._t2_period[1]])
                    bt = Backtest(
                        stk_price_dict[ticker],
                        BuyAndHold,
                        commission=commission,
                        exclusive_orders=True,
                        trade_on_close=True # 可以在訊號觸發當天收盤價買
                    )

                # 布林通道策略
                elif self.window_config['strategy'] == 2:
                    # 傳入均線長度與寬度
                    BBands.set_param(BBands, self._ma_len,  self._band_width)
                    bt = Backtest(
                        stk_price_dict[ticker],
                        BBands,
                        commission=commission,
                        exclusive_orders=True,
                        trade_on_close=True # 可以在訊號觸發當天收盤價買
                    )

                result = bt.run()
                # print(result)
                # bt.plot()
                
                return {ticker: {
                    'equity_df': result['_equity_curve'].loc[strat_date: end_date][['Equity']],
                    'trade_df': result['_trades'],
                }}
            except Exception as e:
                print("[ticker {}]: <{} to {}> {}".format(
                    ticker, self._t2_period[0], self._t2_period[1], e)
                )
                return {ticker: {
                    'equity_df': pd.DataFrame(),
                    'trade_df': pd.DataFrame(),
                }}
        
        # 因為有使用 inner function 所以要使用 pathos 的 multiprocessing 而非 python 原生的
        # Pool() 不放參數則默認使用電腦核的數量
        pool = pathos.multiprocessing.Pool()
        results = pool.map(multiprocessing_job, self._group_ticker) 
        pool.close()
        pool.join()

        return results

    def _create_equity_table(self):
        stk_price_dict = self._get_stk_price()
        results = self._run_backtest(stk_price_dict)
        
        fail_ticker_list = []
        trade_dict = {}

        # 整理預先回測好的 每日權益變化 與 每筆交易
        for result in results:
            ticker = list(result.keys())[0]
            equity_df = list(result.values())[0]['equity_df']
            trade_df = list(result.values())[0]['trade_df']

            # 紀錄回測失敗標的
            if equity_df.empty and trade_df.empty:
                fail_ticker_list.append({
                    'ticker': ticker,
                    'equity_df': equity_df,
                    'trade_df': trade_df, 
                })

            # 其他執行合併每日權益變化 以及取交易開始與結束時間
            else:
                equity_df.columns = [ticker]

                if self.equity_table.empty:
                    self.equity_table = equity_df
                else:
                    self.equity_table = self.equity_table.join(equity_df)

                # 同個窗格內同個標的可能會進出很多次
                trade_list = []
                for i, row in trade_df.iterrows():
                    trade_list.append([row['EntryTime'], row['ExitTime']])
                
                trade_dict[ticker] = trade_list
        
        # 將所有回測失敗標的補空值
        if len(fail_ticker_list) != 0:
            # 取第一個column做為參考 把值都轉成空值
            df = self.equity_table[[self.equity_table.columns[0]]].copy()
            df.loc[:, self.equity_table.columns[0]] = np.nan

            # 然後補在 equity_table 後面
            for result in fail_ticker_list:
                self.equity_table = self.equity_table.join(
                    df.rename(columns={self.equity_table.columns[0]: result['ticker']})
                )

                trade_dict[result['ticker']] = []

        # 依照因子排序的順序來調整column
        self.equity_table = self.equity_table[self._group_ticker]

        return trade_dict

    def _allocate_cash_flow(self, trade_dict):
        # 二維陣列 紀錄每個金流去向
        cash_flow_detail = []

        if self.window_config['strategy'] == 0 or self.window_config['strategy'] == 1:

            for ticker in self._group_ticker:

                if len(self.chosen_ticker) < self.window_config['position']:
                    # 股價不為空 回測有資料 記錄起來
                    if len(trade_dict[ticker]) != 0:
                        # B&H的候選股 = 前position數量的標的 = 選中股
                        self.chosen_ticker.append(ticker)

                        strat_date = trade_dict[ticker][0][0]
                        end_date = trade_dict[ticker][0][1]
                        cash_flow_detail.append([{
                            'ticker': ticker,
                            'unit_equity': self.equity_table.loc[
                                strat_date: end_date, ticker
                            ],
                        }])
                else:
                    break

        elif self.window_config['strategy'] == 2:

            tmep_ticker_list = []
            # 預先創好所有可能會有的金流 陣列位置代表金流編號
            cash_flow_detail = [[] for _ in range(self.window_config['position'])]
            # 編號佇列
            number_queue = [x for x in range(self.window_config['position'])]

            # 每一天每個標的檢查
            for date in self.equity_table.index:

                # 如果目前有持有標的就要檢查 當天是否會出場
                if len(tmep_ticker_list) != 0:
                    for ticker in tmep_ticker_list:
                        strat_date = trade_dict[ticker][0][0]
                        end_date = trade_dict[ticker][0][1]
                        # 代表金流編號 以及 要放在 cash_flow_detail 哪個位置
                        number = trade_dict[ticker][0][2]

                        if date == end_date:
                            # 空出一個位置 等待尋找新標的
                            tmep_ticker_list.remove(ticker)
                            number_queue.append(number)
                            trade_dict[ticker].pop(0)

                for ticker in self._group_ticker:

                    if len(trade_dict[ticker]) != 0:
                        strat_date = trade_dict[ticker][0][0]
                        end_date = trade_dict[ticker][0][1]

                        # 投組還沒裝滿繼續找
                        if len(tmep_ticker_list) < self.window_config['position']:
                            # 標的不重複 且 今天=進場時間
                            if ticker not in tmep_ticker_list and date == strat_date:
                                # 找到新標的 發號碼牌 紀錄資料
                                tmep_ticker_list.append(ticker)
                                number = number_queue.pop(0)
                                trade_dict[ticker][0].append(number)
                                cash_flow_detail[number].append({
                                    'ticker': ticker,
                                    'unit_equity': self.equity_table.loc[
                                        strat_date: end_date, ticker
                                    ],
                                })
                                if ticker not in self.chosen_ticker:
                                    self.chosen_ticker.append(ticker)
                        else:
                            break
                    else:
                        continue

        return cash_flow_detail

    def _allocate_weight(self, cash_flow_detail):
        if self.window_config['if_first'] == True:
            performance_df = pd.DataFrame(
                columns=['ticker', 'start', 'end', 'start_equity', 'final_equity', 'return']
            )
            equity_df = pd.DataFrame(columns=['date', 'portfolio_equity'])
        else:
            # 後面的窗格直接讀即可
            performance_df = self.window_config['performance_df']
            equity_df = self.window_config['equity_df']

        window_equity_df = pd.DataFrame()

        for i, flow in enumerate(cash_flow_detail):
            df = self.equity_table[[self.equity_table.columns[0]]].copy()
            df.loc[:, self.equity_table.columns[0]] = np.nan
            df.columns = [i]

            weight = self.window_config['cash'] / len(cash_flow_detail)

            for trade in flow:
                trade_df = trade['unit_equity']

                scale = weight / trade_df.iloc[0]
                trade_df = trade_df.multiply(scale)

                performance_df = performance_df.append({
                    'ticker': trade['ticker'],
                    'start': trade_df.index[0],
                    'end': trade_df.index[-1],
                    'start_equity': trade_df.iloc[0],
                    'final_equity': trade_df.iloc[-1],
                    'return': (trade_df.iloc[-1]-trade_df.iloc[0])/trade_df.iloc[0]*100,
                }, ignore_index=True)

                df.loc[trade_df.index[0]: trade_df.index[-1], df.columns[0]] = trade_df

                weight = trade_df.iloc[-1]

            window_equity_df = df if window_equity_df.empty else window_equity_df.join(df)
        
        window_equity_df = window_equity_df.fillna(method='ffill').fillna(method='bfill')
        window_equity_df['portfolio_equity'] = window_equity_df.iloc[:, :].sum(axis=1)
        
        equity_record = window_equity_df[['portfolio_equity']].reset_index().to_dict('records')
        equity_df = equity_df.append(equity_record, ignore_index=True)
        
        self.window_config['performance_df'] = performance_df
        self.window_config['equity_df'] = equity_df
