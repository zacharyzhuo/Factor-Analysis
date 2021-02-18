import time
from utils.config import Config
from utils.dbmgr import DBMgr
from utils.general import General
from service.calendar import Calendar
from service.factor import Factor
from modules.my_asset import MyAsset
from analysis.analysis import Analysis


class FactorAnalysisTask:
    def __init__(self, task_list):
        self._task_list = task_list

        self._cfg = Config()
        self._dbmgr = DBMgr()
        self._general = General()

        # 將task_list中每一筆子任務的細節抓出來
        self.task_list_detail = self._get_task_list_detail()
        self.factor_list = self._get_factor_list()

    def _get_task_list_detail(self):
        sql = " SELECT  * \
                FROM    `task_status` \
                WHERE   "
        args = {}

        for task_status in self._task_list:
            label = 'task_status_id_' + str(task_status)
            if task_status == self._task_list[-1]:
                sql = sql + "`task_status_id`=%({})s".format(label)
            else:
                sql = sql + "`task_status_id`=%({})s OR ".format(label)
            args[label] = str(task_status)

        status, row, data = self._dbmgr.query(sql, args, fetch='all')
        return data if data else {}

    def _get_factor_list(self):
        factor_list = []

        # 找出不重複的因子
        for i, task_detail in enumerate(self.task_list_detail):
            self.task_list_detail[i]['factor'] = self._general.string_to_list(task_detail['factor'])
            for factor in task_detail['factor']:
                if factor not in factor_list:
                    factor_list.append(factor)
        return factor_list
