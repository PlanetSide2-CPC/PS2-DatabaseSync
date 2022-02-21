"""应用的高层实现代码。"""
import asyncio

from websockets.exceptions import WebSocketException
from loguru import logger

from hydrogen.websocket import Websocket

while True:
    try:
        asyncio.run(Websocket().connect())

    except KeyboardInterrupt:
        logger.info("进程被用户关闭。")
        break

    except WebSocketException:
        logger.warning("连接失败，尝试重新连接。")
        continue

    except asyncio.TimeoutError:
        logger.warning("异步 IO 超时，尝试重新连接")
        continue

    except OSError as exception:
        continue
