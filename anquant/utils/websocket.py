# -*— coding:utf-8 -*-
import asyncio
import zlib

import aiohttp

from anquant.tasks import SingleTask
from anquant.utils import logger
from anquant.config import config
from anquant.heartbeat import heartbeat
from anquant.utils.locker import async_method_locker


class WebSocket:

    def __init__(self, url=None, check_conn_interval=10, send_hb_interval=10):
        self._url = url
        self._ws = None
        self._check_conn_interval = check_conn_interval
        self._send_hb_interval = send_hb_interval
        self.heartbeat_msg = None

    def initialize(self):
        heartbeat.register(self._check_connection, self._check_conn_interval)
        heartbeat.register(self._send_heartbeat_msg, self._send_hb_interval)
        asyncio.get_event_loop().create_task(self._connect())

    async def _connect(self):
        logger.info("url:", self._url, caller=self)
        proxy = config.proxy
        session = aiohttp.ClientSession()
        try:
            self._ws = await session.ws_connect(self._url, proxy=proxy)
        except Exception as e:
            logger.error("connect to server error! url:", self._url, e, caller=self)
            return
        asyncio.get_event_loop().create_task(self.connected_callback())
        asyncio.get_event_loop().create_task(self.receive())

    @async_method_locker("WebSocket.check_connection", wait=False)
    async def _check_connection(self, *args, **kwargs):
        if not self._ws:
            logger.warn("websocket connection not connected yet!", caller=self)
            await asyncio.get_event_loop().create_task(self._reconnect())
            return
        if self._ws.closed:
            logger.warn("websocket connection closed!", caller=self)
            await asyncio.get_event_loop().create_task(self._reconnect())
            return

    async def connected_callback(self):
        raise NotImplementedError

    async def _reconnect(self):
        logger.warn("reconnecting websocket right now!", caller=self)
        await self._connect()

    async def receive(self):
        async for msg in self._ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                await asyncio.get_event_loop().create_task(self.process(msg.data))
            elif msg.type == aiohttp.WSMsgType.BINARY:
                await asyncio.get_event_loop().create_task(self.process_binary(msg.data))
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                logger.warn("receive event CLOSED:", msg, caller=self)
                await asyncio.get_event_loop().create_task(self._reconnect())
                return
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error("receive event ERROR:", msg, caller=self)
            else:
                logger.warn("unhandled msg:", msg, caller=self)

    async def process(self, msg):
        raise NotImplementedError

    async def process_binary(self, raw):
        """ 处理websocket上接收到的消息
        @param raw 原始的压缩数据
        """
        decompress = zlib.decompressobj(-zlib.MAX_WBITS)
        msg = decompress.decompress(raw)
        msg += decompress.flush()
        await self.process(msg.decode())

    async def _send_heartbeat_msg(self, *args, **kwargs):
        if self.heartbeat_msg:
            if isinstance(self.heartbeat_msg, dict):
                await self._ws.send_json(self.heartbeat_msg)
            elif isinstance(self.heartbeat_msg, str):
                await self._ws.send_str(self.heartbeat_msg)
            else:
                logger.error("send heartbeat msg failed! heartbeat msg:", self.heartbeat_msg, caller=self)
                return
            logger.debug("send ping message:", self.heartbeat_msg, caller=self)