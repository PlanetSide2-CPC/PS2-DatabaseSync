import asyncio
import json
import logging.config
import logging.handlers
import os

import pymysql
import websockets


class Mysql(object):
    """数据库相关操作

    """

    def __init__(self):
        with open("config/database.json") as config:
            database = json.load(config)

        self.conn = pymysql.connect(host=database["host"], port=database["port"], db=database["database"],
                                    user=database["user"], password=database["password"])

    async def update_event_in_background(self, payload):
        pass


class DeathEventHandler(Mysql):
    """死亡事件

    """

    async def update_event_in_background(self, payload):
        """击杀数据库更新

        :param payload: Websocket 订阅数据，字典类。
        """
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

        develop_logger.debug(f"UPDATE {payload}")


class AlertEventHandler(Mysql):
    """警报事件

    """

    async def update_event_in_background(self, payload):
        """警报数据库更新

        :param payload: Websocket 订阅数据，字典类。
        """
        with self.conn.cursor() as cursor:
            sql = "INSERT INTO ps2_jingbao (faction_vs, faction_tr, faction_nc, world_id, zone_id, " \
                  "metagame_event_id, metagame_event_state) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (payload["faction_vs"], payload["faction_tr"], payload["faction_nc"],
                                 payload["world_id"], payload["zone_id"], payload["metagame_event_id"],
                                 payload["metagame_event_state"]))
            self.conn.commit()

        develop_logger.debug(f"UPDATE {payload}")


class Subscription(object):
    """同步订阅事件至数据库，使用 Websockets

    """

    def __init__(self):
        # Websocket API 订阅内容，http://census.daybreakgames.com/
        self.ps_api = "wss://push.planetside2.com/streaming?environment=ps2&service-id=s:yinxue"
        self.subscribe = '{"service":"event","action":"subscribe","characters":["all"],"eventNames":["Death", ' \
                         '"MetagameEvent"],"worlds":["1", "10", "13", "17", "40"],' \
                         '"logicalAndCharactersWithWorlds":true} '
        self.death_handler = DeathEventHandler()
        self.alert_handler = AlertEventHandler()

    async def connect_ps_api(self):
        """连接行星边际 API 接口，并调用更新方法同步数据

        """
        async with websockets.connect(self.ps_api, ping_timeout=None) as ws:
            production_logger.info("Connection established.")
            await ws.send(self.subscribe)
            while True:
                message = await ws.recv()
                data: dict = json.loads(message)

                await self.sync_data_to_database(data)

    async def sync_data_to_database(self, data):
        """同步数据至数据库

        :param data: API 返回数据
        """
        is_subscription_event = True and data.get("service") == "event" and data.get("type") == "serviceMessage"

        if is_subscription_event:
            await self.match_event_name(data)

    async def match_event_name(self, data):
        """匹配事件对应的数据库操作

        :param data: API 返回数据
        """
        payload: dict = data["payload"]

        if payload.get("event_name") == "Death":
            await self.death_handler.update_event_in_background(payload)

        elif payload.get("event_name") == "MetagameEvent":
            await self.alert_handler.update_event_in_background(payload)


if __name__ == '__main__':
    current_file_path = os.path.dirname(__file__)
    os.chdir(current_file_path)

    log_folder = "log"
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # 从文件中读取日志配置
    with open("config/logging.json", "r") as logging_config_file:
        logging_config = json.load(logging_config_file)

    logging.config.dictConfig(logging_config)
    develop_logger = logging.getLogger("develop")
    production_logger = logging.getLogger("production")

    synchronize = Subscription()

    while True:
        try:
            asyncio.run(synchronize.connect_ps_api())

        except KeyboardInterrupt:
            production_logger.info("The program was closed by the user.")
            break

        except websockets.WebSocketException:
            production_logger.warning("Connection failed, try to reconnect.")
            continue
