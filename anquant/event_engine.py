# -*— coding:utf-8 -*-
import asyncio
import json

import aioamqp

from anquant.tasks import LoopTask, SingleTask
from anquant.utils import logger
from anquant.utils.locker import async_method_locker


class Event:
    def __init__(self, name=None, exchange=None, queue=None, routing_key=None, pre_fetch_count=1, data=None):
        self._name = name
        self._exchange = exchange
        self._queue = queue
        self._routing_key = routing_key
        self._pre_fetch_count = pre_fetch_count
        self._data = data
        self._callback = None

    @property
    def name(self):
        return self._name

    @property
    def exchange(self):
        return self._exchange

    @property
    def queue(self):
        return self._queue

    @property
    def routing_key(self):
        return self._routing_key

    @property
    def prefetch_count(self):
        return self._pre_fetch_count

    @property
    def data(self):
        return self._data

    def dumps(self):
        d = {
            "n": self.name,
            "d": self.data
        }
        return json.dumps(d)

    def loads(self, b):
        d = json.loads(b)
        self._name = d.get("n")
        self._data = d.get("d")
        return d

    def parse(self):
        raise NotImplemented

    def subscribe(self, callback, multi=False):
        from anquant import quant
        self._callback = callback
        SingleTask.run(quant.event_engine.subscribe, self, self.callback, multi)

    def publish(self):
        from anquant import quant
        SingleTask.run(quant.event_engine.publish, self)

    async def callback(self, exchange, routing_key, body):
        self._exchange = exchange
        self._routing_key = routing_key
        self.loads(body)
        await self._callback(self.parse())

    def __str__(self):
        info = "EVENT: name={n}, exchange={e}, queue={q}, routing_key={r}, data={d}".format(
            e=self.exchange, q=self.queue, r=self.routing_key, n=self.name, d=self.data)
        return info

    def __repr__(self):
        return str(self)


class EventEngine:
    def __init__(self, rabbitmq_config):
        self._host = rabbitmq_config.get("host", "127.0.0.1")
        self._port = rabbitmq_config.get("port", 5672)
        self._username = rabbitmq_config.get("username", "guest")
        self._password = rabbitmq_config.get("password", "guest")
        self._protocol = None
        self._channel = None
        self._connected = False
        self._subscribers = []
        self._event_handler = {}
        LoopTask.register(self._check_connect, 10)
        asyncio.get_event_loop().run_until_complete(self.connect())

    async def _check_connect(self, *args, **kwargs):
        """
        check connect
        :param interval:
        :return:
        """
        if self._connected and self._channel and self._channel.is_open:
            logger.debug("check server connection OK", caller=self)
            return
        logger.error("connection lose! start reconnect  ...", caller=self)
        self._connected = False
        self._protocol = None
        self._channel = None
        self._event_handler = {}
        SingleTask.run(self.connect, reconnect=True)

    async def _check_subscriber(self, *args, **kwargs):
        pass

    async def connect(self, reconnect=False):
        """
        build tcp connection
        :param reconnect:
        :return:
        """
        logger.info("host:", self._host, "port:", self._port, caller=self)
        if self._connected:
            return

        # connect
        try:
            transport, protocol = await aioamqp.connect(host=self._host, port=self._port,
                                                        login=self._username, password=self._password)
        except Exception as e:
            logger.error("connect error:", e, caller=self)
            return
        finally:
            if self._connected:
                return
        channel = await protocol.channel()
        self._protocol = protocol
        self._channel = channel
        self._connected = True
        logger.info("rabbitmq initialize success!", caller=self)

        # default exchange
        exchanges = ["Orderbook", "Trade", "Kline", "Ticker", ]
        for name in exchanges:
            await self._channel.exchange_declare(exchange_name=name, type_name="topic")
        logger.info("create default exchanges success!", caller=self)

        if reconnect:
            self._bind_consume()
        else:
            asyncio.get_event_loop().call_later(5, self._bind_consume)

    def _bind_consume(self):
        async def do_them():
            for event, callback, multi in self._subscribers:
                await self._initialize(event, callback, multi)

        SingleTask.run(do_them)

    async def _initialize(self, event: Event, callback=None, multi=False):
        """
        create/bind exchange message queue
        :param event:
        :param callback:
        :param multi:
        :return:
        """
        if event.queue:
            await self._channel.queue_declare(queue_name=event.queue)
            queue_name = event.queue
        else:
            result = await self._channel.queue_declare(exclusive=True)
            queue_name = result["queue"]
        await self._channel.queue_bind(queue_name=queue_name, exchange_name=event.exchange,
                                       routing_key=event.routing_key)
        await self._channel.basic_qos(prefetch_count=event.prefetch_count)
        if callback:
            if multi:
                await self._channel.basic_consusme(callback=callback, queue_name=queue_name, no_ack=True)
                logger.info("multi message queue:", queue_name, "callback:", callback, caller=self)
            else:
                await self._channel.basic_consume(self._on_consume_event_msg, queue_name=queue_name)
                logger.info("queue:", queue_name, caller=self)
                self._add_event_handler(event, callback)

    async def _on_consume_event_msg(self, channel, body, envelope, properties):
        """
        receive subscribe message
        :param channel:
        :param body:
        :param envelope:
        :param properties:
        :return:
        """
        logger.debug("exchange:", envelope.exchange_name, "routing_key:", envelope.routing_key,
                     "body:", body, caller=self)
        try:
            key = "{exchange}:{routing_key}".format(exchange=envelope.exchange_name, routing_key=envelope.routing_key)
            funcs = self._event_handler[key]
            for func in funcs:
                SingleTask.run(func, envelope.exchange_name, envelope.routing_key, body)
        except:
            logger.error("event handle error! body:", body, caller=self)
            return
        finally:
            await self._channel.basic_client_ack(delivery_tag=envelope.delivery_tag)

    def _add_event_handler(self, event: Event, callback):
        """
        add event handler function
        :param event:
        :param callback:
        :return:
        """
        key = "{exchange}:{routing_key}".format(exchange=event.exchange, routing_key=event.routing_key)
        if key in self._event_handler:
            self._event_handler[key].append(callback)
        else:
            self._event_handler[key] = [callback]
        logger.info("event handlers:", self._event_handler, caller=self)

    @async_method_locker("EventEngine.subscribe")
    async def subscribe(self, event: Event, callback=None, multi=False):
        """
        register event
        :param event:
        :param callback:
        :param multi:
        :return:
        """
        logger.info("NAME:", event.name, "EXCHANGE:", event.exchange, "QUEUE:", event.queue,
                    "ROUTING_KEY:", event.routing_key, caller=self)
        self._subscribers.append((event, callback, multi))

    async def publish(self, event):
        """
        publish event
        :param event:
        :return:
        """
        if not self._connected:
            logger.warn("rabbitmq not ready right now!", caller=self)
            return
        data = event.dumps()
        logger.debug("exchange_name", event.exchange, "routing_key", event.routing_key, "data", data)
        await self._channel.basic_publish(payload=bytes(data, encoding="utf8"), exchange_name=event.exchange,
                                          routing_key=event.routing_key)
