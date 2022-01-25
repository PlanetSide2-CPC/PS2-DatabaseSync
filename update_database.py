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

    async def update_death_event(self, payload):
        """击杀数据库更新

        :param payload: Websocket 订阅数据，字典类。
        """
        # 数据库更新
        with self.conn.cursor() as cursor:
            sql = "INSERT INTO ps2_death (attacker_character_id, attacker_fire_mode_id, attacker_loadout_id, " \
                  "attacker_vehicle_id, attacker_weapon_id, character_id, character_loadout_id, is_headshot, " \
                  "world_id, zone_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (payload["attacker_character_id"], payload["attacker_fire_mode_id"],
                                 payload["attacker_loadout_id"], payload["attacker_vehicle_id"],
                                 payload["attacker_weapon_id"], payload["character_id"],
                                 payload["character_loadout_id"], payload["is_headshot"],
                                 payload["world_id"], payload["zone_id"]))
            self.conn.commit()

        print(payload)

    async def update_alert_event(self, payload):
        """ 警报数据库更新

        :param payload: Websocket 订阅数据，字典类。
        """
        # 数据库更新
        print(payload)


async def connect_websocket():
    # Websocket API 订阅内容，http://census.daybreakgames.com/
    ps_api = "wss://push.planetside2.com/streaming?environment=ps2&service-id=s:yinxue"
    subscribe = '{"service":"event","action":"subscribe","characters":["all"],"eventNames":["Death", ' \
                '"MetagameEvent"],"worlds":["1", "10", "13", "17", "40"],"logicalAndCharactersWithWorlds":true} '
    # 连接数据库
    mysql = Mysql()

    async with websockets.connect(ps_api, ping_timeout=None) as websocket:
        await websocket.send(subscribe)
        print("Pending for message...")

        while True:
            message = await websocket.recv()
            data: dict = json.loads(message)

            # 是否为订阅事件
            if not (True and data.get("service") == "event" and data.get("type") == "serviceMessage"):
                continue

            # 判断事件选择数据库操作
            payload: dict = data["payload"]

            if payload.get("event_name") == "Death":
                await mysql.update_death_event(payload)

            elif payload.get("event_name") == "MetagameEvent":
                await mysql.update_alert_event(payload)


if __name__ == '__main__':
    while True:
        try:
            asyncio.run(connect_websocket())

        except KeyboardInterrupt:
            break

        except websockets.WebSocketException:
            continue
