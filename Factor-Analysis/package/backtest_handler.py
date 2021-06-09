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
from weight.fixed_target import FixedTarget
from weight.dynamic_target import DynamicTarget


class BacktestHandler:

    def __init__(self, window_config, cal, fac):
        self.window_config = window_config
        self._cal = cal
        self._fac = fac

        self._period = []
        self.group_ticker = [] # 該群排序完的標的
        self._cfg = Config()
        
        self._optimized_param = {}
        self._profit_table = pd.DataFrame()
        self._weight_table = pd.DataFrame()
    
    def t1_optimize(self, t1_period, group_ticker):
        self._period = t1_period
        self.group_ticker = group_ticker

        if self.window_config['strategy'] != 0:
            # 最佳化每支候選股 並存下最佳化參數
            stk_price_dict = self._get_stk_price(self._period)
            results = self._run_backtest(stk_price_dict, if_optimize=True)

            # 製作最佳化參數字典
            for result in results:
                ticker = list(result.keys())[0]
                ma_len = result[ticker]['strategy']['ma_len']
                band_width = result[ticker]['strategy']['band_width']
                self._optimized_param[ticker] = {
                    'ma_len': ma_len,
                    'band_width': band_width,
                }
            # print(self._optimized_param)
    
    def t2_backtest(self, t2_period):
        self._period = t2_period
        max_ma = int(self._cfg.get_value('parameter', 'max_ma'))
        last_date = self._cfg.get_value('parameter', 'end_date')

        # 買入持有策略
        if self.window_config['strategy'] == 0:
            # 因為 backtesting 不能在第一天跟最後一天交易 所以必須往前後多加一天
            start_date = self._cal.get_trade_date(self._period[0], -2, 'd')

        # 動態換股策略
        elif self.window_config['strategy'] == 1:
            # 因為要算均線所以要往前多抓幾天
            start_date = self._cal.get_trade_date(self._period[0], (1+max_ma)*-1, 'd')
        
        if self._period[1] < last_date:
            # 必須要往後多抓一天 不然第一天跟最後一天不能交易
            end_date = self._cal.get_trade_date(self._period[1], 1, 'd')
        
        else:
            end_date = last_date

        stk_price_dict = self._get_stk_price([start_date, end_date])
        results = self._run_backtest(stk_price_dict)
        trade_dict = self._create_profit_table(stk_price_dict, results)
        cash_flow, reallocated_date = self._create_weight_table(trade_dict)
        self._create_performance_table(cash_flow, reallocated_date)

    def _get_stk_price(self, period):
        api_server_IP = self._cfg.get_value('IP', 'api_server_IP')
        payloads = {
            'ticker_list': self.group_ticker,
            'start_date': period[0],
            'end_date': period[1],
        }
        response = requests.get("http://{}/stk/get_ticker_period_stk".format(api_server_IP), params=payloads)
        stk_price_dict = json.loads(response.text)['result']

        for ticker in self.group_ticker:
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

    def _run_backtest(self, stk_price_dict, if_optimize=False):
        min_ma = int(self._cfg.get_value('parameter', 'min_ma'))
        max_ma = int(self._cfg.get_value('parameter', 'max_ma'))
        ma_step = int(self._cfg.get_value('parameter', 'ma_step'))
        min_band_width = float(self._cfg.get_value('parameter', 'min_band_width'))
        max_band_width = float(self._cfg.get_value('parameter', 'max_band_width'))
        band_width_step = float(self._cfg.get_value('parameter', 'band_width_step'))

        # 使用 inner function 特別獨立出需要多核運算的部分
        def multiprocessing_job(ticker):
            try:
                # 買入持有策略
                if self.window_config['strategy'] == 0:
                    # 傳入窗格開始與結束時間 即買點與賣點
                    BuyAndHold.set_param(BuyAndHold, [self._period[0]],  [self._period[1]])
                    bt = Backtest(
                        stk_price_dict[ticker],
                        BuyAndHold,
                        exclusive_orders=True,
                        trade_on_close=True # 可以在訊號觸發當天收盤價買
                    )
                    result = bt.run()

                    return {ticker: {
                        'trade_df': result['_trades'],
                    }}

                # 動態換股策略
                elif self.window_config['strategy'] == 1:
                    # 是否為最佳化找參數
                    if if_optimize:
                        BBands.set_param(BBands, min_ma, min_band_width, self._period[0])
                        bt = Backtest(
                            stk_price_dict[ticker],
                            BBands,
                            exclusive_orders=True,
                            trade_on_close=True # 可以在訊號觸發當天收盤價買
                        )
                        result = bt.optimize(
                            ma_len=range(min_ma, max_ma+ma_step, ma_step),
                            band_width=[round(x, 1) for x in np.arange(
                                min_band_width, max_band_width+band_width_step, band_width_step
                            )],
                        )
                    
                    else:
                        # 固定參數
                        if self.window_config['window'] == 0:
                            ma_len = int(self._cfg.get_value('parameter', 'ma_len'))
                            band_width = float(self._cfg.get_value('parameter', 'band_width'))

                        # 套用最佳化參數
                        elif self.window_config['window'] == 1 or self.window_config['window'] == 2:
                            ma_len = self._optimized_param[ticker]['ma_len']
                            band_width = self._optimized_param[ticker]['band_width']

                        # period參數: 有多往前算均線 但必須在窗格開始第一天之後才能買
                        BBands.set_param(BBands, ma_len, band_width, self._period[0])
                        bt = Backtest(
                            stk_price_dict[ticker],
                            BBands,
                            exclusive_orders=True,
                            trade_on_close=True # 可以在訊號觸發當天收盤價買
                        )
                        result = bt.run()
                
                    return {ticker: {
                        'strategy': {
                            'ma_len': result['_strategy'].ma_len,
                            'band_width': result['_strategy'].band_width,
                        },
                        'trade_df': result['_trades'],
                    }}
            except Exception as e:
                # print("[ticker {}]: <{} to {}> {}".format(
                #     ticker, self._period[0], self._period[1], e)
                # )
                return {ticker: {
                    'strategy': {
                        'ma_len': None,
                        'band_width': None,
                    },
                    'trade_df': pd.DataFrame(),
                }}
        
        # 因為有使用 inner function 所以要使用 pathos 的 multiprocessing 而非 python 原生的
        # Pool() 不放參數則默認使用電腦核的數量
        pool = pathos.multiprocessing.Pool()
        results = pool.map(multiprocessing_job, self.group_ticker) 
        pool.close()
        pool.join()

        return results

    def _create_profit_table(self, stk_price_dict, results):
        fail_ticker_list = []
        trade_dict = {}

        # 整理預先回測好的 每日權益變化 與 每筆交易
        for result in results:
            ticker = list(result.keys())[0]
            trade_df = result[ticker]['trade_df']

            # 回測失敗的標的不納入排名
            if trade_df.empty:
                self.group_ticker.remove(ticker)

            # 其他執行合併每日權益變化 以及取交易開始與結束時間
            else:
                # 用收盤價來算賺賠 並調整範圍
                stk_df = stk_price_dict[ticker][['Close']].loc[
                    self._period[0]: self._period[1]
                ]
                stk_df['shift'] = stk_df['Close'].shift()
                # [(今日收盤 - 昨日收盤)/ 昨日收盤] + 1
                stk_df = ((stk_df['Close']-stk_df['shift'])/stk_df['shift'] + 1).to_frame()
                stk_df.columns = [ticker]

                # 抓此窗格內的所有交易日
                trade_date_list = self._cal.get_period_trade_date(self._period[0], self._period[1])

                if self._profit_table.empty:
                    # 以這些交易日做好profit_table的框
                    self._profit_table['date'] = trade_date_list
                    # 拼接每個標的的賺賠
                    self._profit_table = self._profit_table.set_index('date').join(stk_df)
                
                else:
                    self._profit_table = self._profit_table.join(stk_df)

                # 同個窗格內同個標的可能會進出很多次
                trade_list = []
                for i, row in trade_df.iterrows():
                    trade_list.append([row['EntryTime'], row['ExitTime']])
                
                trade_dict[ticker] = trade_list
                
        # 依照因子排序的順序來調整column
        self._profit_table = self._profit_table[self.group_ticker]

        return trade_dict

    def _create_weight_table(self, trade_dict):
        method = self.window_config['method']

        # 買入持有
        if self.window_config['strategy'] == 0:
            self._weight_table, cash_flow, reallocated_date = FixedTarget(
                self.window_config, self._profit_table, trade_dict
            ).get_weight(method=method)

        # 動態換股
        elif self.window_config['strategy'] == 1:
            self._weight_table, cash_flow, reallocated_date = DynamicTarget(
                self.window_config, self._profit_table, trade_dict
            ).get_weight(method=method)
        
        return cash_flow, reallocated_date

    def _create_performance_table(self, cash_flow, reallocated_date):
        # df = self._weight_table.dropna(axis=1, how='all')
        # print(df)

        # 初次窗格先創建預設 df
        if self.window_config['is_first'] == True:
            portfo_perf = pd.DataFrame(
                columns=['ticker', 'start', 'end', 'start_equity', 'final_equity', 'return', 'flow']
            )
            portfo_equity = pd.DataFrame(columns=['date', 'total'])
        # 後面的窗格直接讀即可
        else:
            portfo_perf = self.window_config['portfolio_performance']
            portfo_equity = self.window_config['portfolio_equity']

        performance_table = pd.DataFrame()
        portfolio_cash = self.window_config['cash']
        commission = float(self._cfg.get_value('parameter', 'commission'))
        # 紀錄每個金流中 目前該筆交易的初始資產
        first_equity_queue = [0 for x in range(len(cash_flow))]
        # 紀錄每個金流中 持有標的的每日權益值 (每天覆蓋)
        flow_cash_queue = [0 for x in range(len(cash_flow))]
        # 紀錄該天有哪個金流發生出場動作
        if_exit_queue = []
        daily_equity = 0

        # 每天檢查
        for date in self._profit_table.index:
            # 當天績效
            performance_dict = {}
            performance_dict['date'] = date
            temp_daily_equity = [0 for x in range(len(cash_flow))]

            # 如果該天不用重新分配權重
            if date not in reallocated_date:

                # 每天檢查每個金流的持有標的
                for i, flow in enumerate(cash_flow):
                    if flow:
                        ticker = flow[0]['ticker']
                        start_date = flow[0]['start_date']
                        end_date = flow[0]['end_date']
                        weight = self._weight_table.loc[date, ticker]

                        # 某金流中 第一個被分配權重的那天
                        if date == start_date and type(weight) == float:
                            # 按照投組目前總資金乘上分配到的權重
                            equity = portfolio_cash * weight
                            # 計算進場手續費
                            equity = equity * (1 - commission)
                            first_equity_queue[i] = equity
                            flow_cash_queue[i] = equity
                            performance_dict[i] = equity
                            temp_daily_equity[i] = equity
                        
                        # 繼續持有當中包含出場當天
                        elif date > start_date and date <= end_date and weight == '-':
                            profit = self._profit_table.loc[date, ticker]
                            equity = flow_cash_queue[i] * profit

                            # 當天出場
                            if date == end_date:
                                # 計算出場手續費
                                equity = equity * (1 - commission)
                                portfo_perf = portfo_perf.append({
                                    'ticker': ticker,
                                    'start': start_date,
                                    'end': end_date,
                                    'start_equity': first_equity_queue[i],
                                    'final_equity': equity,
                                    'return': (equity-first_equity_queue[i])/first_equity_queue[i]*100,
                                    'flow': i,
                                }, ignore_index=True)
                                # 刪除已計算完成的交易
                                cash_flow[i].pop(0)
                                if_exit_queue.append(i)

                            flow_cash_queue[i] = equity
                            performance_dict[i] = equity
                            temp_daily_equity[i] = equity

                        # 上一個金流的賺賠直接歐印新標的
                        elif date == start_date and weight == '-':
                            # 計算進場手續費
                            equity = flow_cash_queue[i] * (1 - commission)
                            first_equity_queue[i] = equity
                            flow_cash_queue[i] = equity
                            performance_dict[i] = equity
                            temp_daily_equity[i] = equity
                
                # 當天投組有部位出場
                if len(if_exit_queue) != 0:
                    # 檢查出場的部位
                    for j in if_exit_queue:
                        # 排除該部位已經是最後一筆交易情況
                        if len(cash_flow[j]) != 0:
                            start_date = cash_flow[j][0]['start_date']
                            # 原部位出場的當天又有新部位進場
                            if date == start_date:
                                # 計算進場手續費
                                equity = flow_cash_queue[j] * (1 - commission)
                                first_equity_queue[j] = equity
                                flow_cash_queue[j] = equity
                                performance_dict[j] = equity
                                temp_daily_equity[j] = equity
                # 當天執行完清空陣列
                if_exit_queue = []

                if sum(temp_daily_equity) != 0:
                    daily_equity = sum(temp_daily_equity)

            # 要重新分配權重
            else:
                # 紀錄計算完該天賺賠後的初始賺賠 以後續計算回補手續費
                org_equity_list = [0 for x in range(len(cash_flow))]

                # 加總目前投組的權益
                for i, flow in enumerate(cash_flow):
                    if flow:
                        ticker = flow[0]['ticker']
                        start_date = flow[0]['start_date']
                        end_date = flow[0]['end_date']
                        weight = self._weight_table.loc[date, ticker]
                        
                        if date > start_date and date <= end_date:
                            profit = self._profit_table.loc[date, ticker]
                            equity = flow_cash_queue[i] * profit
                            # 計算出場手續費
                            equity = equity * (1 - commission)
                            org_equity_list[i] = equity

                            if date == end_date:
                                portfo_perf = portfo_perf.append({
                                    'ticker': ticker,
                                    'start': start_date,
                                    'end': end_date,
                                    'start_equity': first_equity_queue[i],
                                    'final_equity': equity,
                                    'return': (equity-first_equity_queue[i])/first_equity_queue[i]*100,
                                    'flow': i,
                                }, ignore_index=True)
                                # 刪除已計算完成的交易
                                cash_flow[i].pop(0)
                                flow_cash_queue[i] = equity
                
                # 判斷是否為該窗格第一筆被分配權重的交易
                first_flag = True if sum(flow_cash_queue) == 0 else False

                # 按照該分配的比例分配
                for i, flow in enumerate(cash_flow):
                    if flow:
                        ticker = flow[0]['ticker']
                        start_date = flow[0]['start_date']
                        end_date = flow[0]['end_date']
                        weight = self._weight_table.loc[date, ticker]

                        # 權重分配當天有持有部位 包含當天出場的部位
                        if sum(org_equity_list) != 0:
                            if date == start_date:
                                equity = sum(org_equity_list) * weight
                                # 計算進場手續費
                                equity = equity * (1 - commission)
                                first_equity_queue[i] = equity
                                flow_cash_queue[i] = equity
                                performance_dict[i] = equity
                            
                            elif date > start_date and date < end_date:
                                equity = sum(org_equity_list) * weight
                                payable_commission = abs(org_equity_list[i]-equity)
                                paid_commission = org_equity_list[i]
                                receivable_commission = (paid_commission-payable_commission)*commission
                                equity = equity + receivable_commission
                                flow_cash_queue[i] = equity
                                performance_dict[i] = equity
                        
                        # 權重分配當天未持有部位 代表空手一段時間後找到新標的 或者在窗格第一筆權重分配
                        else:
                            # 窗格第一筆權重分配
                            if first_flag == True:
                                equity = portfolio_cash * weight
                            else:
                                equity = daily_equity * weight

                            if date == start_date:
                                # 計算進場手續費
                                equity = equity * (1 - commission)
                                first_equity_queue[i] = equity
                                flow_cash_queue[i] = equity
                                performance_dict[i] = equity
            
            performance_table = performance_table.append(performance_dict, ignore_index=True)

        performance_table = performance_table.set_index('date')

        # 等權重分配: 錢不會在金流之間跳動
        if len(reallocated_date) == 0:

            # 如果動態換股沒有買滿 要補上這些沒用到的錢
            if len(performance_table.columns) != len(cash_flow):
                cash_not_use = portfolio_cash / len(cash_flow)

                for i in range(len(performance_table.columns)+1, len(cash_flow)+1):
                    performance_table[i] = cash_not_use

            performance_table = performance_table.fillna(method='ffill').fillna(method='bfill')
            performance_table['total'] = performance_table.iloc[:, :].sum(axis=1)
        
        # 資金最大化利用分配: 錢會不斷的重新分配
        else:
            performance_table['total'] = performance_table.iloc[:, :].sum(axis=1).replace({0: np.nan})
            performance_table = performance_table.fillna(method='ffill').fillna(method='bfill')

        equity_record = performance_table[['total']].reset_index().to_dict('records')
        # 串接績效
        portfo_equity = portfo_equity.append(equity_record, ignore_index=True)
        # 重新賦值
        self.window_config['portfolio_performance'] = portfo_perf
        self.window_config['portfolio_equity'] = portfo_equity
        # print(performance_table)
