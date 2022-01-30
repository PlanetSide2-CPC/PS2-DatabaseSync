import asyncio
import json
import logging.config
import logging.handlers
import os

import websockets

import mysql_controller


class Subscription(object):
    """同步订阅事件至数据库，使用 Websockets

    """

    def __init__(self):
        # Websocket API 订阅内容，http://census.daybreakgames.com/
        self.ps_api = "wss://push.planetside2.com/streaming?environment=ps2&service-id=s:yinxue"
        self.subscribe = '{"service":"event","action":"subscribe","characters":["all"],"eventNames":["Death", ' \
                         '"MetagameEvent"],"worlds":["1", "10", "13", "17", "40"],' \
                         '"logicalAndCharactersWithWorlds":true} '
        self.death_handler = mysql_controller.DeathEventHandler()
        self.alert_handler = mysql_controller.AlertEventHandler()

    async def connect_ps_api(self):
        """连接行星边际 API 接口，并调用更新方法同步数据

        """
        async with websockets.connect(self.ps_api, ping_timeout=None) as ws:
            logger.info("Connection established.")
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
            await self.select_event_handler(data)

    async def select_event_handler(self, data):
        """匹配事件对应的数据库操作

        :param data: API 返回数据
        """
        payload: dict = data["payload"]

        if payload.get("event_name") == "Death":
            await self.death_handler.update_event_in_background(payload)

        elif payload.get("event_name") == "MetagameEvent":
            await self.alert_handler.update_event_in_background(payload)


def setup_logging():
    with open("config/logging.json", "r") as logging_config_file:
        logging_config = json.load(logging_config_file)

    logging.config.dictConfig(logging_config)

    return logging.getLogger()


if __name__ == '__main__':
    current_file_path = os.path.dirname(__file__)
    os.chdir(current_file_path)

    logger = setup_logging()
    synchronize = Subscription()

    while True:
        try:
            asyncio.run(synchronize.connect_ps_api())

        except KeyboardInterrupt:
            logger.info("The program was closed by the user.")
            break

        except websockets.WebSocketException:
            logger.warning("Connection failed, try to reconnect.")
            continue
