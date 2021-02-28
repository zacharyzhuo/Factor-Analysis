import time
from utils.dbmgr import DBMgr
from utils.general import General
from task.factor_analysis_handler import FactorAnalysisHandler
from node.node_handler import NodeHandler
from msg.host_msg_handler import HostMsgHandler


class FactorAnalysisTaskHandler:

    def __init__(self, request):
        self._request = request

        self._task_list = []
        self._task_id = -1

        self._factor_analysis_handler = FactorAnalysisHandler()
        self._node_handler = NodeHandler()
        self._dbmgr = DBMgr()
        self._general = General()

    # 自動分配排程工作
    def schedule_task(self):
        # 抓出未完成未完成的任務組合
        status, task_id, task_list = self._factor_analysis_handler.check_unfinished_task()
        # 檢查此 request 是否與過去的任務相同
        exist_status, exist_task_id = self._factor_analysis_handler.check_exist_task(self._request)

        # 有未完成的任務
        if status:
            self._task_id = task_id
            self._task_list = task_list
            print("[FactorAnalysisTaskHandler] 執行尚未完成任務，任務編號：{}；任務清單：{}".format(task_id, task_list))
            self._request = self._factor_analysis_handler.get_request(task_id)
        # 如沒有未完成的任務，再檢查是否有已經完成之相同任務
        elif exist_status:
            self._task_id = exist_task_id
            print("[FactorAnalysisTaskHandler] 資料庫內已經有完成之任務 編號：{}".format(self._task_id))
        # 需要創建不同組合工作
        else:
            # 將各種 request 之參數排列組合成一個2D陣列
            combination = self._general.combinate_parameter(
                self._request['factor_list'],
                self._request['strategy_list'],
                self._request['group_list'],
                self._request['position_list']
            )
            # 將 request 轉換成任務新增至 DB ，並取得 task_id
            self._task_id = self._factor_analysis_handler.add_task_to_db(self._request)
            # 將所有任務的組合新增至 DB
            self._factor_analysis_handler.add_task_detail_to_db(self._task_id, combination)
            self._task_list = self._factor_analysis_handler.get_all_task_list_by_status(self._task_id)

        task_id = self._task_id
        task_list = self._task_list

        if not exist_status or status:
            # 直到全部任務完成才出去
            while True:
                self._distribute_to_node(task_id, task_list)
                # 檢查是否仍有未完成任務
                status, task_id, task_list = self._factor_analysis_handler.check_unfinished_task()
                # 確認所有任務完成
                if not status:
                    break
                print("[FactorAnalysisTaskHandler] 仍有未完成任務 編號:{} ;任務細節編號:{}".format(task_id, task_list))

        self._request["isFinish"] = 1
        self._request['task_id'] = self._task_id
        self._task_list = self._factor_analysis_handler.get_all_task_list(self._task_id)
        self._request['task_list'] = self._task_list
        return self._request

    def _distribute_to_node(self, task_id, task_list):
        self._node_handler.clean_all_node_data()
        # 發送狀態確認並更新狀態
        self._node_handler.check_node_status()
        # 檢查所有節點狀態 是否死亡
        if not self._node_handler.check_node_health():
            self._node_handler.clean_all_node_data()
            self._node_handler.check_node_status()

        # 取得所有運算節點
        nodes = self._node_handler.get_node_status()
        if len(nodes) == 0:
            print("[FactorAnalysisTaskHandler] 目前沒有存活的節點，但任務尚未發送完畢")
        else:
            batch_task_slice_list = self._node_handler.distribute_batch_task(len(task_list), len(nodes))
            for i, node in enumerate(nodes):
                # 判斷節點是否已經有工作 避免重複發送
                if self._factor_analysis_handler.check_node_have_task(node['name']):
                    continue
                # 判斷節點是否為正常無工作 且健康狀態發送新任務
                elif node['health'] == 0:
                    batch_task_list = task_list[batch_task_slice_list[i][0]:batch_task_slice_list[i][1]]
                    # MQTT 發送任務
                    print("node name: ", node['name'])
                    HostMsgHandler().publish_processing_task(node['name'], task_id, batch_task_list)
                    # 更新任務持有者
                    self._factor_analysis_handler.update_task_owner(node['name'], batch_task_list)
                    # 更新節點狀態為「執行中」
                    self._node_handler.update_node_status(node['name'], 1)
                else:
                    continue
        time.sleep(30)
        # 0：無任務
        # 1：執行中
        # 2：節點已死亡
        # 檢查節點是否還有在運算 (超過10分鐘未回應即判斷死亡)
        while self._node_handler.check_node_health():
            print("[FactorAnalysisTaskHandler] 檢查各運算節點")
            self._node_handler.publish_node_health_check()
            # 判斷所有節點是否已經完成（即為全部為 0 或 2）
            if self._node_handler.check_all_node_finish():
                print("[FactorAnalysisTaskHandler] 全部節點已經運算完成或死亡")
                break
            # 若仍有節點在運算中 間隔300秒(5分鐘)檢查一次
            time.sleep(300)
            print("[FactorAnalysisTaskHandler] 仍有節點在運算 持續檢查健康度")
