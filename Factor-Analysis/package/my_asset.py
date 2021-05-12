import os
import pandas as pd
import json
from package.portfolio import Portfolio
from utils.config import Config
from utils.general import General


class MyAsset:

    def __init__(self, strategy_config, cal, fac):
        self._strategy_config = strategy_config
        self._cal = cal
        self._fac = fac
        
        self._cfg = Config()
        self._path = self._cfg.get_value('path', 'path_to_portfolio_performance')
        self._general = General()

        self._factor_str = self._general.factor_to_string(self._strategy_config['factor'])

        self._show_task_detail()
        self._portfolio = Portfolio(self._strategy_config, self._cal, self._fac)
        self._write_portfolio_performance()
    
    def _show_task_detail(self):
        columns_list = [
            'factor', 'strategy', 'window', 'method', 'group', 
            'position', 'n_season', 'start_equity', 'period'
        ]

        df = pd.DataFrame().append({
            'factor': self._factor_str,
            'strategy': self._strategy_config['strategy'],
            'window': self._strategy_config['window'], 
            'method': self._strategy_config['method'], 
            'group': self._strategy_config['group'],
            'position': self._strategy_config['position'],
            'n_season': int(self._cfg.get_value('parameter', 'n_season')),
            'start_equity': int(self._cfg.get_value('parameter', 'start_equity')),
            'period': "from {} to {}".format(
                self._cfg.get_value('parameter', 'start_date'),
                self._cfg.get_value('parameter', 'end_date')
            )
        }, ignore_index=True)[columns_list]
        print(df.set_index('factor').T)
    
    def _write_portfolio_performance(self):
        portfolio_performance, portfolio_equity = self._portfolio.get_performance_data()
        path = self._path + self._factor_str

        # e.g. MOM_0_0_1_5 or MOM&GVI_1_0_1_5
        file_name = "{}_{}_{}_{}_{}_{}".format(
            self._factor_str,
            str(self._strategy_config['strategy']),
            str(self._strategy_config['window']),
            str(self._strategy_config['method']),
            str(self._strategy_config['group']),
            str(self._strategy_config['position'])
        )

        # 如果沒有這個因子的資料夾就新增一個
        if not os.path.exists(path):
            os.makedirs(path)

        path = "{}/{}".format(path, file_name)
        portfolio_performance.to_csv(path + '.csv', header=True)

        portfolio_equity['date'] = portfolio_equity['date'].dt.strftime('%Y-%m-%d')
        with open(path + '.json', 'w') as file:
            json.dump(portfolio_equity.to_dict(), file)
        print('[MyAsset]: completed writing portfolio performance files')
