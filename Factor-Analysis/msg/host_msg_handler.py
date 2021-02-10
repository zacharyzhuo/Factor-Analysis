import getpass
import json
import os
import random
import socket
import time
import paho.mqtt.client as paho
import paho.mqtt.publish as publish
from datetime import datetime
from utils.config import Config
from utils.dbmgr import DBMgr


class HostMsgHandler:

    def __init__(self):
        self._cfg = Config()
        self._dbmgr = DBMgr()

        self._processes = os.cpu_count()  # 伺服器CPU核心數
        self._server_name = getpass.getuser()  # 伺服器使用者名稱
        self._ip = socket.gethostbyname(socket.gethostname())
        self._host_IP = self._cfg.get_value('IP', 'host_IP')
        self._share_folder_IP = self._cfg.get_value('IP', 'share_folder_IP')
        self.client_ID = self._server_name + "_" + self._ip
        self._mqtt_account = self._cfg.get_value('MQTT', 'account')
        self._mqtt_password = self._cfg.get_value('MQTT', 'password')
        self._db_data = self._cfg.get_database()

    # (Subscribe) 訂閱所有回傳的 TOPIC
    def subscribe_respond(self):
        mqtt_client = self.client_ID + " StatusRespond and FinishTask"  # 設定節點名稱
        
        client = paho.Client(client_id=mqtt_client, clean_session=False)
        client.message_callback_add("Analysis/StatusRespond", self._handle_status_update)
        client.message_callback_add("Analysis/HealthResponse", self._handle_health_update)
        client.message_callback_add("Analysis/FinishTask", self._handle_finish_task)
        client.username_pw_set(self._mqtt_account, self._mqtt_password)
        client.connect(self._host_IP, 1883)
        # 開啟另一個
        client.loop_start()
        client.subscribe("Analysis/#", qos=2)

    # (Publish) 發送節點狀態確認訊息
    def publish_status_check(self):
        mqtt_client = self.client_ID + " StatusCheck"  # 設定節點名稱

        # 送出狀態確認訊息，
        payload = {
            "message": "StatusCheck"
        }
        payload = json.dumps(payload)
        publish.single(
            qos=2,
            keepalive=60,
            payload=payload,
            client_id=mqtt_client,
            topic="Analysis/StatusCheck",
            hostname=self._host_IP,
            auth={
                'username': self._mqtt_account,
                'password': self._mqtt_password
            }
        )
        print("[HostMsgHandler] Host Status Check.....")

    # (CallBack) 處理狀態確認任務完成訊息
    # input: client   : 發送訊息的節點ID
    #        userdata : 資料型態
    #        msg      : 訊息內容
    def _handle_status_update(self, client, userdata, msg):
        # MQTT CallBack參數取出
        node_msg = self._phase_mqtt_msg(msg)
        print("[HostMsgHandler] get {} Status Check Respond".format(node_msg['node_name']))
        current_time = str(datetime.now())

        sql = "SELECT * FROM `node` WHERE name = %(name)s"
        args = {"name": str(node_msg['node_name'])}
        status, row, result = self._dbmgr.query(sql, args)

        # 新增節點
        if row == 0:
            sql = " INSERT INTO `node` \
                    VALUES      ('0', %(name)s, %(cpu_status)s, %(core_num)s, %(health)s, %(health_time)s)"
            args = {
                "name": str(node_msg['node_name']),
                "cpu_status": str(node_msg['node_cpu_status']),
                "core_num": str(node_msg['node_core_number']),
                "health": '0',
                "health_time": current_time
            }
            status, row, result = self._dbmgr.insert(sql, args)
            print("[HostMsgHandler] add a new node: {}".format(node_msg['node_name']))
        # 更新節點
        else:
            sql = " UPDATE  `node` \
                    SET     `cpu_status`=%(cpu_status)s, `core_num`=%(core_num)s, `health`=%(health)s, \
                            `health_time`=%(health_time)s \
                    WHERE   `name`=%(name)s"
            args = {
                "name": str(node_msg['node_name']),
                "cpu_status": str(node_msg['node_cpu_status']),
                "core_num": str(node_msg['node_core_number']),
                "health": '0',
                "health_time": current_time
            }
            status, row, result = self._dbmgr.update(sql, args)
            print("[HostMsgHandler] update node: {}".format(node_msg['node_name']))

    def _handle_health_update(self, client, userdata, msg):
        # MQTT CallBack參數取出
        node_msg = self._phase_mqtt_msg(msg)
        current_time = str(datetime.now())

        sql = "SELECT * FROM `node` WHERE name = %(name)s"
        args = {"name": str(node_msg['node_name'])}
        status, row, result = self._dbmgr.query(sql, args)

        # 新增節點
        if row == 0:
            sql = " INSERT INTO `node` \
                    VALUES      ('0', %(name)s, %(cpu_status)s, %(core_num)s, %(health)s, %(health_time)s)"
            args = {
                "name": str(node_msg['node_name']),
                "cpu_status": str(node_msg['node_cpu_status']),
                "core_num": str(node_msg['node_core_number']),
                "health": '1',
                "health_time": current_time
            }
            status, row, result = self._dbmgr.insert(sql, args)

        # 更新節點
        else:
            sql = " UPDATE  `node` \
                    SET     `cpu_status`=%(cpu_status)s, `core_num`=%(core_num)s, `health`=%(health)s, \
                            `health_time`=%(health_time)s \
                    WHERE   `name`=%(name)s"
            args = {
                "name": str(node_msg['node_name']),
                "cpu_status": str(node_msg['node_cpu_status']),
                "core_num": str(node_msg['node_core_number']),
                "health": '1',
                "health_time": current_time
            }
            status, row, result = self._dbmgr.update(sql, args)

    def publish_processing_task(self, node_name, task_id, task_list):
        mqtt_client = self.client_ID + "FactorAnalysisTaskPublish"  # 設定節點名稱
        payload = {
            'owner': node_name,  # 負責任務之節點ID
            'task_list': task_list,  # 任務細節編號
        }
        payload = json.dumps(payload)
        publish.single(
            qos=2,
            keepalive=60,
            payload=payload,
            client_id=mqtt_client,
            topic="Analysis/FactorAnalysisTask",
            hostname=self._host_IP,
            auth={
                'username': self._mqtt_account,
                'password': self._mqtt_password
            }
        )
        print("[HostMsgHandler] send Task...", "Node: ", node_name, "  taskID: ", task_id, " task_list:", task_list)

    def _handle_finish_task(self, client, userdata, msg):
        # status
        # 0 - undo
        # 1 - success
        # 2 - error
        # MQTT CallBack參數取出
        node_msg = self._phase_mqtt_msg(msg)
        current_time = str(datetime.now())
        print('node_msg: ', node_msg)

        sql = " UPDATE  `task_status` \
                SET     `finish_time`=%(finish_time)s, `owner`=%(owner)s, `status`=%(status)s \
                WHERE   `task_status_id`=%(task_status_id)s"
        args = {
            "finish_time": current_time,
            "owner": str(node_msg['node_name']),
            "status": str(node_msg['status']),
            "task_status_id": str(node_msg['task_status_id']),
        }
        status, row, result = self._dbmgr.update(sql, args)
        print("[HostMsgHandler] {} Node is Finsh {} has been updated to DB".format(node_msg['node_name'], node_msg['task_status_id']))

    def _phase_mqtt_msg(self, msg):
        node_msg = str(msg.payload, encoding="utf-8")
        node_msg = json.loads(node_msg)
        return node_msg
