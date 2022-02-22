"""Websocket 连接模块。"""
import json

import websockets

from loguru import logger

from hydrogen.shortcuts import read_config
from hydrogen.database import MysqlFactory, MongodbFactory


class Websocket:
    """Websocket 连接接口。"""

    def __init__(self):
        self.seperator = ', '

        self.character = read_config('character')
        self.events = self.seperator.join(read_config('events'))
        self.worlds = self.seperator.join(read_config('worlds'))

        # 添加工厂实例化
        if read_config('source') == 'mysql':
            self.database = MysqlFactory().create_database()
        elif read_config('source') == 'mongodb':
            self.database = MongodbFactory().create_database()
        else:
            raise Exception("配置文件的 source 数据库类型未存在或错误")

    def __repr__(self):
        return "API 连接实例初始化成功"

    async def connect(self):
        """连接到行星边际 API。"""
        async with websockets.connect(read_config('service'), ping_timeout=None) as websocket:
            await self.on_connect(websocket)

    async def on_connect(self, connect):
        """连接时订阅事件。

        Args:
            connect: 连接对象。

        Returns: None

        """
        logger.info("连接已建立，请求订阅数据")
        subscription = '{' + f'"service":"event","action":"subscribe",' \
                             f'"characters":[{self.character}],"eventNames":[{self.events}],' \
                             f'"worlds":[{self.worlds}],"logicalAndCharactersWithWorlds":true' + '}'
        await connect.send(subscription)
        while True:
            message = await connect.recv()
            loads_message = json.loads(message)

            await self.is_service_message(loads_message)

    async def is_service_message(self, loads_message):
        """是否是订阅的服务信息。

        如果是订阅事件，则提交信息至数据库。

        Args:
            loads_message (dict): 返回信息

        Returns: None

        """
        if 'serviceMessage' in loads_message.values():
            payload = loads_message.get('payload')
            self.database.update(payload.get('event_name'), payload)
