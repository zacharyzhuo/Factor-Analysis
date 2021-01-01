from modules.calendar import Calendar
from modules.factor import Factor
from modules.portfolio import Portfolio


class MyStrategy:
    def __init__(self, strategy, optimization_setting, weight_setting, factor_name,
                group, position, start_equity, start_date, end_date):
        self.strategy = strategy
        self.optimization_setting = optimization_setting
        self.weight_setting = weight_setting
        self.factor_name = factor_name
        self.group = group
        self.position = position
        self.start_equity = start_equity
        self.start_date = start_date
        self.end_date = end_date
        
        self.cal = Calendar('TW')
        self.portfolio = None
        self.create_portfolio()
    
    def get_ticker_list(self):
        print('doing get_ticker_list...')
        date = self.cal.advance_date(self.start_date, 1, 's')
        print('backtesting period: ' + self.start_date + ' to ' + self.end_date)
        print('get factor data at ' + date)
        self.factor = Factor(self.factor_name, date)
        print(self.factor.factor_df)
        ranking_list = self.factor.rank_factor()
        print('get group ' + str(self.group) + ' from ranking list')
        ticker_group_df = ranking_list[self.group - 1]
        print(ticker_group_df)
        print('get a ticker list of top ' + str(self.position) + ' from group ' + str(self.group))
        ticker_list = ticker_group_df['ticker'].iloc[0: self.position].tolist()
        print('ticker_list: ', ticker_list)
        return ticker_list
    
    def create_portfolio(self):
        print('doing create_portfolio...')
        ticker_list = self.get_ticker_list()
        print('creating a portfolio and loading ticker list data')
        self.portfolio = Portfolio(self.cal,
                                   self.strategy,
                                   self.optimization_setting,
                                   self.weight_setting,
                                   self.factor_name,
                                   self.start_equity,
                                   self.start_date,
                                   self.end_date,
                                   ticker_list)
