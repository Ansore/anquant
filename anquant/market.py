# -*- coding:utf-8 -*-
import json

from anquant import constant


class Ticker:
    def __init__(self, platform=None, symbol=None, last_price=None, last_size=None,
                 ask_price=None, ask_size=None, bid_price=None, bid_size=None, timestamp=None):
        self.platform = platform
        self.symbol = symbol
        self.last_price = last_price
        self.last_size = last_size
        self.ask_price = ask_price
        self.ask_size = ask_size
        self.bid_price = bid_price
        self.bid_size = bid_size
        self.timestamp = timestamp

    @property
    def data(self):
        return {
            "platform": self.platform,
            "symbol": self.symbol,
            "last_price": self.last_price,
            "last_size": self.last_size,
            "ask_price": self.ask_price,
            "ask_size": self.ask_size,
            "bid_price": self.bid_price,
            "bid_size": self.bid_size,
            "timestamp": self.timestamp
        }

    def load_data(self, d):
        self.platform = d["platform"]
        self.symbol = d["symbol"]
        self.last_price = d["last_price"]
        self.last_size = d["last_size"]
        self.ask_price = d["ask_price"]
        self.ask_size = d["ask_size"]
        self.bid_price = d["bid_price"]
        self.bid_size = d["bid_size"]
        self.timestamp = d["timestamp"]
        return self

    def __str__(self):
        return json.dumps(self.data)

    def __repr__(self):
        return str(self)


class Orderbook:
    def __init__(self, platform=None, symbol=None, asks=None, bids=None, timestamp=None):
        """
        :param platform:
        :param symbol:
        :param asks:
        :param bids:
        :param timestamp:
        """
        self.platform = platform
        self.symbol = symbol
        self.asks = asks
        self.bids = bids
        self.timestamp = timestamp

    @property
    def data(self):
        return {
            "platform": self.platform,
            "symbol": self.symbol,
            "asks": self.asks,
            "bids": self.bids,
            "timestamp": self.timestamp
        }

    def load_data(self, d):
        self.platform = d["platform"]
        self.symbol = d["symbol"]
        self.asks = d["asks"]
        self.bids = d["bids"]
        self.timestamp = d["timestamp"]
        return self

    def __str__(self):
        return json.dumps(self.data)

    def __repr__(self):
        return str(self)


class Trade:
    def __init__(self, platform=None, symbol=None, action=None, price=None, quantity=None, timestamp=None):
        self.platform = platform
        self.symbol = symbol
        self.action = action
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp

    @property
    def data(self):
        d = {
            "server_id": self.server_id,
            "platform": self.platform,
            "symbol": self.symbol,
            "action": self.action,
            "price": self.price,
            "quantity": self.quantity,
            "timestamp": self.timestamp
        }
        return d

    def load_data(self, d):
        self.platform = d["platform"]
        self.symbol = d["symbol"]
        self.action = d["action"]
        self.price = d["price"]
        self.quantity = d["quantity"]
        self.timestamp = d["timestamp"]
        return self

    def __str__(self):
        info = json.dumps(self.data)
        return info

    def __repr__(self):
        return str(self)


class Kline:
    def __init__(self, platform=None, symbol=None, open=None, high=None, low=None, close=None,
                 volume=None, timestamp=None, kline_type=None):

        self.platform = platform
        self.symbol = symbol
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.timestamp = timestamp
        self.kline_type = kline_type

    @property
    def data(self):
        return {
            "platform": self.platform,
            "symbol": self.symbol,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "timestamp": self.timestamp,
            "kline_type": self.kline_type
        }

    def load_data(self, d):
        self.platform = d["platform"]
        self.symbol = d["symbol"]
        self.open = d["open"]
        self.high = d["high"]
        self.low = d["low"]
        self.close = d["close"]
        self.volume = d["volume"]
        self.timestamp = d["timestamp"]
        self.kline_type = d["kline_type"]
        return self

    def __str__(self):
        info = json.dumps(self.data)
        return info

    def __repr__(self):
        return str(self)


class Market:
    def __init__(self, market_type, platform, symbol, callback):
        if platform == "#" or symbol == "#":
            multi = True
        else:
            multi = False
        if market_type == constant.MARKET_TYPE_KLINE:
            from anquant.event import EventKline
            EventKline(Kline(platform, symbol, kline_type=market_type)).subscribe(callback, multi)
        if market_type == constant.MARKET_TYPE_TRADE:
            from anquant.event import EventTrade
            EventTrade(Trade(platform, symbol)).subscribe(callback, multi)
        if market_type == constant.MARKET_TYPE_ORDERBOOK:
            from anquant.event import EventOrderbook
            EventOrderbook(Orderbook(platform, symbol)).subscribe(callback, multi)
