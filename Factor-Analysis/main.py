from modules.mystrategy import MyStrategy
from modules.analysis import Analysis


strategy = [0, 1]                           # 0: BuyAndHold; 1: KTNChannel
optimization_setting = [0, 1]               # 0: 無變數(or單一變數); 1: 最佳化變數
weight_setting = [0, 1, 2]                  # 0: equal_weight; 1: equal_risk(ATR); 2: equal_risk(SD)
factor_name = ['GVI', 'EPS', 'MOM', 'PE', 'EV_EBITDA', 'EV_S', 'FC_P', 'CROIC', 'FC_OI', 'FC_LTD']
group = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
position = [5, 10, 15, 30, 90, 150]
start_equity = 10000000
start_date = '2010-01-01'
end_date = '2017-12-31'
risk_free_rate = 0.01


my_stra = MyStrategy(strategy=strategy[0],
                    optimization_setting=optimization_setting[0],
                    weight_setting=weight_setting[0],
                    factor_name=factor_name[2],
                    group=group[0],
                    position=position[0],
                    start_equity=start_equity,
                    start_date=start_date,
                    end_date=end_date)


# analysis = Analysis(start_equity, start_date, end_date, risk_free_rate)
                  


        