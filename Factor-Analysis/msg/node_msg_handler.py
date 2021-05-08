import getpass
import json
import os
import psutil
import socket
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
from datetime import datetime
from utils.config import Config
from utils.dbmgr import DBMgr
from task.factor_analysis_task import FactorAnalysisTask
from service.calendar import Calendar
from service.factor import Factor
from package.my_asset import MyAsset


class NodeMsgHandler:

    def __init__(self):
        self._cfg = Config()
        self._dbmgr = DBMgr()

        # 基本參數 (伺服器設定值)
        self._processes = os.cpu_count()  # 伺服器CPU核心數
        self._server_name = getpass.getuser()  # 伺服器使用者名稱
        self._IP = socket.gethostbyname(socket.gethostname())
        self._host_IP = self._cfg.get_value('IP', 'host_IP')
        self.client_ID = self._server_name + "_" + self._IP
        self._mqtt_account = self._cfg.get_value('MQTT', 'account')
        self._mqtt_password = self._cfg.get_value('MQTT', 'password')

    def active_mqtt(self):
        mqtt_client = self.client_ID + " ProcessTask"  # 設定節點名稱
        client = mqtt.Client(client_id=mqtt_client)
        client.on_connect = self._on_connect
        client.on_message = self._on_message

        client.username_pw_set(self._mqtt_account, self._mqtt_password)
        client.connect(self._host_IP, 1883)
        # 開始連線 執行設定的動作和處理重新連線問題
        client.loop_forever()

    def _on_connect(self, client, userdata, flag, rc):
        print("Connected with result code {}".format(str(rc)))
        # 0: 連接成功
        # 1: 協議版本錯誤
        # 2: 無效的客戶端標示
        # 3: 伺服器無法使用
        # 4: 使用者帳號或密碼錯誤
        # 5: 未經授權

        # 將訂閱主題寫在 on_connect 中，當重新連線時將會重新訂閱
        client.subscribe("Analysis/FactorAnalysisTask", qos=2)
        client.subscribe("Analysis/StatusCheck", qos=2)
        client.subscribe("Analysis/HealthCheck", qos=2)

    def _on_message(self, client, userdata, msg):
        if msg.topic == "Analysis/FactorAnalysisTask":
            self._handle_factor_analysis_task(client, userdata, msg)
        elif msg.topic == "Analysis/StatusCheck":
            self._status_receive(client, userdata, msg)
        elif msg.topic == "Analysis/HealthCheck":
            self._health_receive(client, userdata, msg)

    # (CallBack) 處理狀態確認訊息
    # input: client   : 發送訊息的節點ID
    #        userdata : 資料型態
    #        msg      : 訊息內容
    def _status_receive(self, client, userdata, msg):
        print("Receive Status Check and Respond...")
        self._publish_status_respond()

    # (Publish) 回傳節點系統狀態
    def _publish_status_respond(self):
        mqtt_client = self.client_ID + " StatusRespond"  # 設定節點名稱

        # 轉換Json格式
        payload = {
            'node_name': self.client_ID,
            'node_core_number': self._processes,
            'node_cpu_status': psutil.cpu_percent()
        }
        payload = json.dumps(payload)
        # 送出訊息
        publish.single(qos=2,
                       keepalive=60,
                       payload=payload,
                       topic="Analysis/StatusRespond",
                       client_id=mqtt_client,
                       hostname=self._host_IP,
                       auth={'username': self._mqtt_account,
                             'password': self._mqtt_password}
                    )
        print('%s publish status respond' % self.client_ID)

    # (CallBack) 處理健康狀態確認訊息
    # input: client   : 發送訊息的節點ID
    #        userdata : 資料型態
    #        msg      : 訊息內容
    def _health_receive(self, client, userdata, msg):
        print("Receive Health Check and Respond...")
        self._publish_health_respond()

    # (Publish) 回傳節點系統狀態
    def _publish_health_respond(self):
        mqtt_client = self.client_ID + " HealthResponse"  # 設定節點名稱

        # 轉換Json格式
        payload = {
            'node_name': self.client_ID,
            'node_core_number': self._processes,
            'node_cpu_status': psutil.cpu_percent(),
        }
        payload = json.dumps(payload)
        # 送出訊息
        publish.single(qos=2,
                       keepalive=60,
                       payload=payload,
                       topic="Analysis/HealthResponse",
                       client_id=mqtt_client,
                       hostname=self._host_IP,
                       auth={'username': self._mqtt_account,
                             'password': self._mqtt_password}
                       )
        print('%s publish health request' % self.client_ID)

    # (CallBack) 處理接收到之任務
    # input: client   : 發送訊息的節點ID
    #        userdata : 資料型態
    #        msg      : 訊息內容
    def _handle_factor_analysis_task(self, client, userdata, msg):
        # MQTT CallBack參數取出
        payload = self._phase_mqtt_msg(msg)
        print("task_message = ", payload)
        # 收到指派之任務
        print('task_message["owner"] = ', payload["owner"])
        if payload["owner"] == self.client_ID:
            print("Processing...", str(payload['task_list']))

            factor_analysis_task = FactorAnalysisTask(payload['task_list'])
            task_list_detail = factor_analysis_task.task_list_detail
            factor_list = factor_analysis_task.factor_list
            self._run_factor_analysis(task_list_detail, factor_list)

            time.sleep(10)
            # 全部工作完成 更新節點狀態
            self._change_node_status('0')

    def _run_factor_analysis(self, task_list_detail, factor_list):
        # 預載交易日&因子資料
        cal = Calendar('TW')
        get_factor_start = time.time()
        fac = Factor(factor_list)
        get_factor_end = time.time()
        print("Get factor time: %f second" % (get_factor_end - get_factor_start))

        for task_detail in task_list_detail:
            try:
                start = time.time()
                strategy_config = {
                    'factor': task_detail['factor'],
                    'strategy': task_detail['strategy'],
                    'window': task_detail['window'],
                    'method': task_detail['method'],
                    'group': task_detail['group'],
                    'position': task_detail['position'],
                }
                my_stra = MyAsset(strategy_config, cal, fac)
                end = time.time()
                print("Execution time: %f second" % (end - start))
                
                # status: 0 - undo, 1 - success, 2 - error
                self._publish_factor_analysis_task_finish(task_detail['task_status_id'], 1)
            except Exception as e:
                # status: 0 - undo, 1 - success, 2 - error
                self._publish_factor_analysis_task_finish(task_detail['task_status_id'], 2)
                print(e)

    # (Publish) 回傳節點完成任務
    # status
    # 0 - undo
    # 1 - success
    # 2 - error
    def _publish_factor_analysis_task_finish(self, task_status_id, status):
        mqtt_client = self.client_ID + " StatusRespond"  # 設定節點名稱
        payload = {
            'node_name': self.client_ID,
            'task_status_id': task_status_id,
            'status': status
        }
        payload = json.dumps(payload)
        publish.single(
            qos=2,
            keepalive=60,
            payload=payload,
            topic="Analysis/FinishTask",
            client_id=mqtt_client,
            hostname=self._host_IP,
            auth={
                'username': self._mqtt_account,
                'password': self._mqtt_password
            }
        )

    def _change_node_status(self, health):
        current_time = str(datetime.now())
        sql = " UPDATE  `node` \
                SET     `cpu_status`=%(cpu_status)s, `core_num`=%(core_num)s, \
                        `health`=%(health)s, `health_time`=%(health_time)s \
                WHERE   `name`=%(name)s"
        args = {
            "name": str(self.client_ID),
            "cpu_status": str(psutil.cpu_percent()),
            "core_num": str(self._processes),
            "health": str(health),
            "health_time": current_time
        }
        status, row, result = self._dbmgr.update(sql, args)

    def _phase_mqtt_msg(self, msg):
        node_msg = str(msg.payload, encoding="utf-8")
        node_msg = json.loads(node_msg)
        return node_msg
