import asyncio
import json
import logging

import pymysql
import websockets

logger = logging.getLogger()
logfile = 'test.log'
hdlr = logging.FileHandler('sendlog.txt')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.NOTSET)


class Mysql(object):
    """数据库相关操作

    """

    def __init__(self):
        with open("config/database.json") as config:
            database = json.load(config)
            self.conn = pymysql.connect(host=database["host"], port=database["port"], db=database["database"],
                                        user=database["user"], password=database["password"])

    def update_death_event(self, payload):
        """击杀数据库更新

        :param payload: Websocket 订阅数据，字典类。
        """
        # 数据库更新
        print(payload)

    def update_alert_event(self, payload):
        """ 警报数据库更新

        :param payload: Websocket 订阅数据，字典类。
        """
        # 数据库更新
        print(payload)


async def connect_websocket():
    # Websocket API 订阅内容，http://census.daybreakgames.com/
    ps_api = "wss://push.planetside2.com/streaming?environment=ps2&service-id=s:yinxue"
    subscribe = '{"service":"event","action":"subscribe","characters":["all"],"eventNames":["Death", ' \
                '"MetagameEvent"],"worlds":["40"],"logicalAndCharactersWithWorlds":true} '
    # 连接数据库
    mysql = Mysql()

    async with websockets.connect(ps_api) as websocket:
        await websocket.send(subscribe)
        print("Pending for message...")

        while True:
            message = await websocket.recv()
            data: dict = json.loads(message)

            def is_subscribe_event():
                return True and data.get("service") == "event" and data.get("type") == "serviceMessage"

            if not is_subscribe_event():
                continue

            # 判断事件选择数据库操作
            payload: dict = data["payload"]

            if payload.get("event_name") == "Death":
                mysql.update_death_event(payload)

            if payload.get("event_name") == "MetagameEvent":
                mysql.update_alert_event(payload)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(connect_websocket())
