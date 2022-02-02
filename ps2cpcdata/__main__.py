"""This module implements the core developer interface for ps2cpcdata."""
import asyncio
import json
import logging
import sys

import websockets

from ps2cpcdata import __config__
from ps2cpcdata import database

logging.basicConfig(stream=sys.stderr, level="NOTSET")
logger = logging.getLogger(__name__)


class PS2CPCData(object):
    def __init__(self):
        self.planetside = __config__["planetside2"]
        self.api = self.planetside["api"]
        self.subscription = self.planetside["subscription"]
        self.database = database.Mysql()

    async def connect(self):
        async with websockets.connect(self.api, ping_timeout=None) as ws:
            await ws.send(self.subscription)
            while True:
                message = await ws.recv()
                data = json.loads(message)
                await self.update_database(data)

    async def update_database(self, data):
        try:
            payload = data["payload"]
        except KeyError:
            return

        if "Death" in payload.values():
            await self.database.death(payload)

        elif "MetagameEvent" in payload.values():
            await self.database.alert(payload)


ps2cpc_data = PS2CPCData()

while True:
    try:
        asyncio.run(ps2cpc_data.connect())

    except KeyboardInterrupt:
        logger.info("The program was closed by the user.")
        break

    except websockets.WebSocketException:
        logger.warning("Connection failed, try to reconnect.")
        continue
