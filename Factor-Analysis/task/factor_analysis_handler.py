from datetime import datetime
from utils.dbmgr import DBMgr
from utils.general import General


class FactorAnalysisHandler:

    def __init__(self):
        self._dbmgr = DBMgr()
        self._general = General()

    def add_task_to_db(self, request):
        current_time = str(datetime.now())
        sql = "INSERT INTO `task` \
                VALUES      ('0', %(factor_list)s, %(strategy_list)s, %(window_list)s, %(method_list)s, \
                                    %(group_list)s, %(position_list)s, %(begin_time)s)"
        args = {
            "factor_list": self._general.factor_list_to_string(request['factor_list']),
            "strategy_list": self._general.list_to_string(request['strategy_list']),
            "window_list": self._general.list_to_string(request['window_list']),
            "method_list": self._general.list_to_string(request['method_list']),
            "group_list": self._general.list_to_string(request['group_list']),
            "position_list": self._general.list_to_string(request['position_list']),
            "begin_time": str(current_time),
        }
        status, row, result = self._dbmgr.insert(sql, args)
        task_id = self.get_last_task_id(current_time)
        return task_id

    def add_task_detail_to_db(self, task_id, combination):
        task_result = self.get_task_by_id(task_id)
        args = []

        for task_list in combination:
            factor = task_list[0]
            strategy = task_list[1]
            window = task_list[2]
            method = task_list[3]
            group = task_list[4]
            position = task_list[5]
            args.append({
                "task_id": str(task_id),
                "factor": self._general.list_to_string(factor),
                "strategy": str(strategy),
                "window": str(window),
                "method": str(method),
                "group": str(group),
                "position": str(position),
                "finish_time": str(''),
                "owner": str(''),
                "status": str('0'),
            })

        sql = " INSERT INTO `task_status` \
                VALUES      ('0', %(task_id)s, %(factor)s, %(strategy)s, %(window)s, %(method)s, \
                                    %(group)s, %(position)s, %(finish_time)s, %(owner)s, %(status)s)"
        status, row, result = self._dbmgr.insert(sql, args, multiple=True)

    def check_unfinished_task(self):
        sql = "SELECT `task_status_id`, `task_id` FROM `task_status` WHERE status=%(status)s"
        args = {"status": str('0')}
        status, row, result = self._dbmgr.query(sql, args)

        task_list = []
        # 表示無未完成任務
        if len(result) == 0:
            status = False
            task_id = -1
        # 有未完成任務
        else:
            status = True
            task_id = result[0]['task_id']
            for sub_task in result:
                task_list.append(sub_task['task_status_id'])
        return status, task_id, task_list
    
    def check_exist_task(self, request):
        sql = " SELECT  `task_id` \
                FROM    `task` \
                WHERE   `factor_list` = %(factor_list)s AND \
                        `strategy_list` = %(strategy_list)s AND \
                        `window_list` = %(window_list)s AND \
                        `method_list` = %(method_list)s AND \
                        `group_list` = %(group_list)s AND \
                        `position_list` = %(position_list)s"
        args = {
            "factor_list": self._general.factor_list_to_string(request['factor_list']),
            "strategy_list": self._general.list_to_string(request['strategy_list']),
            "window_list": self._general.list_to_string(request['window_list']),
            "method_list": self._general.list_to_string(request['method_list']),
            "group_list": self._general.list_to_string(request['group_list']),
            "position_list": self._general.list_to_string(request['position_list']),
        }
        status, row, data = self._dbmgr.query(sql, args, fetch='one')
        if status and data and len(data) == 1:
            return True, data['task_id']
        else:
            return False, -1

    def get_request(self, task_id):
        task_info = {}
        plateau_info = {}

        # 取回任務清單
        sql = "SELECT * FROM `task` WHERE `task_id`=%(task_id)s"
        args = {"task_id": str(task_id)}
        status, row, task_info = self._dbmgr.query(sql, args, fetch='one')

        # 該任務不存在
        if row == 0:
            print('[FactorAnalysisHandler] 該任務編號 {} 不存在！'.format(task_id))
            return {
                'task_id': task_id,
                'factor_list': [],
                'strategy_list': [],
                'window_list': [],
                'method_list': [],
                'group_list': [],
                'position_list': [],
            }
        else:
            return {
                'task_id': task_id,
                'factor_list': self._general.factor_string_to_list(task_info['factor_list']),
                'strategy_list': self._general.string_to_list(task_info['strategy_list']),
                'window_list': self._general.string_to_list(task_info['window_list']),
                'method_list': self._general.string_to_list(task_info['method_list']),
                'group_list': self._general.string_to_list(task_info['group_list']),
                'position_list': self._general.string_to_list(task_info['position_list']),
            }

    def get_task_by_id(self, task_id):
        sql = "SELECT * FROM `task` WHERE task_id = %(task_id)s"
        args = {"task_id": str(task_id)}
        status, row, result = self._dbmgr.query(sql, args, fetch='one')
        return result

    def get_last_task_id(self, curr_time):
        sql = "SELECT * FROM `task` WHERE begin_time = %(begin_time)s"
        args = {"begin_time": str(curr_time)}
        status, row, result = self._dbmgr.query(sql, args, fetch='one')
        return result['task_id']

    def get_all_task_list_by_status(self, task_id, status=0):
        sql = "SELECT `task_status_id` FROM `task_status` WHERE status=%(status)s and task_id=%(task_id)s"
        args = {
            "status": str(status),
            "task_id": str(task_id)
        }
        sql_status, row, result = self._dbmgr.query(sql, args)

        task_list = []
        for sub_task in result:
            task_list.append(sub_task['task_status_id'])
        return task_list

    def get_all_task_list(self, task_id):
        sql = "SELECT `task_status_id` FROM `task_status` WHERE task_id=%(task_id)s"
        args = {"task_id": str(task_id)}
        status, row, result = self._dbmgr.query(sql, args)

        task_list = []
        for sub_task in result:
            task_list.append(sub_task['task_status_id'])
        return task_list

    def check_node_have_task(self, node):
        # 檢查這個 node 目前是否有未完成的任務
        sql = " SELECT * \
                FROM `task_status` \
                WHERE `owner` = %(node)s AND `status` = 0"
        args = {'node': node}
        status, row, result = self._dbmgr.query(sql, args)

        if status and row == 0:
            return False
        else:
            return True
    
    def update_task_owner(self, owner, task_list):
        for task in task_list:
            sql = " UPDATE  `task_status` \
                    SET     `owner`=%(owner)s \
                    WHERE   `task_status_id` = %(task_status_id)s"
            args = {
                "owner": str(owner),
                "task_status_id": str(task)
            }
            status, row, result = self._dbmgr.update(sql, args)
