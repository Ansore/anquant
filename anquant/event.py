# -*— coding:utf-8 -*-
from anquant.asset import Asset
from anquant.event_engine import Event
from anquant.market import Kline, Trade, Orderbook, Ticker


class EventHeartbeat(Event):
    EXCHANGE = "heartbeat"
    QUEUE = None
    NAME = "EVENT_HEARTBEAT"

    def __init__(self, server_id=None, count=None):
        self.server_id = server_id
        self.count = count
        data = {
            "server_id": server_id,
            "count": count
        }
        super(EventHeartbeat, self).__init__(data)

    def parse(self):
        self.server_id = self._data.get("server_id")
        self.count = self._data.get("count")


class EventConfig(Event):
    EXCHANGE = "config"
    QUEUE = None
    NAME = "EVENT_CONFIG"

    def __init__(self, server_id=None, params=None):
        routing_key = "{server_id}".format(server_id=server_id)
        self.ROUTING_KEY = routing_key
        self.server_id = server_id
        self.params = params
        data = {
            "server_id": server_id,
            "params": params
        }
        super(EventConfig, self).__init__(data)

    def parse(self):
        """ 解析self._data数据
        """
        self.server_id = self._data.get("server_id")
        self.params = self._data.get("params")


class EventTrade(Event):
    def __init__(self, trade: Trade):
        name = "EVENT_TRADE"
        exchange = "Trade"
        routing_key = "{p}.{s}".format(p=trade.platform, s=trade.symbol)
        queue = "{ex}.{rk}".format(ex=exchange, rk=routing_key)
        super(EventTrade, self).__init__(name, exchange, queue, routing_key, data=trade.data)

    def parse(self):
        trade = Trade(**self.data)
        return trade


class EventOrderbook(Event):
    def __init__(self, orderbook: Orderbook):
        name = "EVENT_ORDERBOOK"
        exchange = "Orderbook"
        routing_key = "{p}.{s}".format(p=orderbook.platform, s=orderbook.symbol)
        queue = "{ex}.{rk}".format(ex=exchange, rk=routing_key)
        super(EventOrderbook, self).__init__(name, exchange, queue, routing_key, data=orderbook.data)

    def parse(self):
        orderbook = Orderbook(**self.data)
        return orderbook


class EventKline(Event):
    EXCHANGE = "Kline"
    QUEUE = None
    NAME = "EVENT_KLINE_1MIN"
    PRE_FETCH_COUNT = 20

    def __init__(self, kline: Kline):
        name = "EVENT_KLINE"
        exchange = "Kline"
        routing_key = "{p}.{s}".format(p=kline.platform, s=kline.symbol)
        queue = "{ex}.{rk}".format(ex=exchange, rk=routing_key)
        super(EventKline, self).__init__(name, exchange, queue, routing_key, data=kline.data)

    def parse(self):
        kline = Kline(**self.data)
        return kline


class EventTicker(Event):
    def __init__(self, ticker: Ticker):
        name = "EVENT_TICKER"
        exchange = "Ticker"
        routing_key = "{p}.{s}".format(p=ticker.platform, s=ticker.symbol)
        queue = "{ex}.{rk}".format(ex=exchange, rk=routing_key)
        super(EventTicker, self).__init__(name, exchange, queue, routing_key, data=ticker.data)

    def parse(self):
        ticker = Ticker(**self.data)
        return ticker


class EventAsset(Event):
    def __init__(self, asset: Asset):
        name = "EVENT_ASSET"
        exchange = "Asset"
        routing_key = "{platform}.{account}".format(platform=asset.platform, account=asset.account)
        queue = "{exchange}.{routing_key}".format(exchange=exchange, routing_key=routing_key)
        super(EventAsset, self).__init__(name, exchange, queue, routing_key, data=asset.data)

    def parse(self):
        return Asset(**self.data)
