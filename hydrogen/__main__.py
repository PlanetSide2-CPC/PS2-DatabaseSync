"""应用的高层实现代码。"""
import asyncio
import logging

from websockets.exceptions import WebSocketException

from hydrogen.websocket import Websocket

logger = logging.getLogger(__name__)

while True:
    try:
        asyncio.run(Websocket().connect())

    except KeyboardInterrupt:
        logger.info("进程被用户关闭。")
        break

    except WebSocketException:
        logger.warning("连接失败，正在尝试重新连接。")
        continue

    except asyncio.TimeoutError:
        logger.warning("异步 IO 超时，正在尝试重新连接")
        continue
