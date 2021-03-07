import time
from datetime import datetime
from utils.config import Config
from utils.dbmgr import DBMgr
from msg.host_msg_handler import HostMsgHandler


class NodeHandler:

    def __init__(self):
        self._cfg = Config()
        self._dbmgr = DBMgr()

    def clean_all_node_data(self):
        # TRUNCATE 移除資料表上的資料列
        sql = "TRUNCATE `node`"
        args = {}
        status, row, status = self._dbmgr.delete(sql, args)

    def check_node_status(self):
        HostMsgHandler().publish_status_check()
        time_out = int(self._cfg.get_value('time', 'status_check'))
        time.sleep(time_out)

    def publish_node_health_check(self):
        HostMsgHandler().publish_health_check()
        time_out = int(self._cfg.get_value('time', 'status_check'))
        time.sleep(time_out)

    def get_node_status(self):
        sql = "SELECT * FROM `node` ORDER BY `cpu_status`"
        args = {}
        status, row, result = self._dbmgr.query(sql, args)
        return result

    def check_node_health(self):
        status = False
        nodes = self.get_node_status()
        for node in nodes:
            current_time = datetime.now()
            nodes_health_time = datetime.strptime(node['health_time'], '%Y-%m-%d %H:%M:%S.%f')
            # 判定超過健康時間
            if float(str((current_time - nodes_health_time).total_seconds())) > float(
                    self._cfg.get_value('time', 'node_health_time')):
                # 更改節點為死亡
                self.update_node_status(node['name'], 2)
            # 還是有活著的 Node
            elif node['health'] != 2:
                status = True
        return status

    def check_all_node_finish(self):
        status = True
        nodes = self.get_node_status()
        for node in nodes:
            if node['health'] == 1:
                status = False
        return status

    def update_node_status(self, node, health):
        # 發完一輪後檢查節點是否健康 (health)
        # 0：無任務
        # 1：執行中
        # 2：節點已死亡
        sql = "UPDATE `node` SET `health` = %(health)s WHERE `name`=%(owner)s"
        args = {
            "owner": str(node),
            "health": str(health)
        }
        status, row, result = self._dbmgr.update(sql, args)

    def distribute_batch_task(self, task_num, node_num):
        # 將任務平分給各個節點 未整除的部分都給最後一個節點
        batch_task_num = task_num // node_num
        # 整除的時候 = 0
        over_task = task_num % node_num
        batch_task_list = []
        
        for i in range(node_num):
            if i == 0: # 第一個
                batch_task_list.append([0, batch_task_num])
            elif i+1 == node_num: # 最後一個
                batch_task_list.append([batch_task_num*i, batch_task_num*(i+1)+over_task])
            else:
                batch_task_list.append([batch_task_num*i, batch_task_num*(i+1)])
        return batch_task_list

