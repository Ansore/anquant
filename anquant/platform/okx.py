# -*— coding:utf-8 -*-
import asyncio
import base64
import copy
import hmac
import json
import time
from urllib.parse import urljoin

from anquant.config import config
from anquant.constant import *
from anquant.tasks import SingleTask
from anquant.event import EventKline, EventTrade, EventOrderbook, EventTicker
from anquant.market import Ticker, Kline, Trade, Orderbook
from anquant.order import *
from anquant.position import Position
from anquant.utils import logger
from anquant.utils.async_http import AsyncHttpRequests
from anquant.utils.websocket import WebSocket

"""
OKX_KLINE_KLINE_1Y = "candle1Y"
OKX_KLINE_KLINE_1M = "candle1M"
OKX_KLINE_KLINE_4M = "candle3M"
OKX_KLINE_KLINE_6M = "candle6M"
OKX_KLINE_KLINE_1W = "candle1W"
OKX_KLINE_KLINE_1D = "candle1D"
OKX_KLINE_KLINE_2D = "candle2D"
OKX_KLINE_KLINE_3D = "candle3D"
OKX_KLINE_KLINE_5D = "candle5D"
OKX_KLINE_KLINE_1H = "candle1H"
OKX_KLINE_KLINE_2H = "candle2H"
OKX_KLINE_KLINE_4H = "candle4H"
OKX_KLINE_KLINE_6H = "candle6H"
OKX_KLINE_KLINE_12H = "candle12H"
OKX_KLINE_KLINE_1MIN = "candle1m"
OKX_KLINE_KLINE_3MIN = "candle3m"
OKX_KLINE_KLINE_5MIN = "candle5m"
OKX_KLINE_KLINE_15MIN = "candle15m"
OKX_KLINE_KLINE_30MIN = "candle30m"
OKX_KLINE_KLINE_2DUTC = "candle2Dutc"
OKX_KLINE_KLINE_3DUTC = "candle3Dutc"
OKX_KLINE_KLINE_5DUTC = "candle5Dutc"
OKX_KLINE_KLINE_12HUTC = "candle12hutc"
OKX_KLINE_KLINE_6HUTC = "candle6hutc"
"""

MARKET_CHANNEL_TRANSFORM = {
    "candle1m": MARKET_KLINE_KLINE_1MIN,
    "candle3m": MARKET_KLINE_KLINE_3MIN,
    "candle5m": MARKET_KLINE_KLINE_5MIN,
    "candle15m": MARKET_KLINE_KLINE_15MIN,
    "candle30m": MARKET_KLINE_KLINE_30MIN,
    "candle1H": MARKET_KLINE_KLINE_1H,
    "candle2H": MARKET_KLINE_KLINE_2H,
    "candle4H": MARKET_KLINE_KLINE_4H,
    "candle6H": MARKET_KLINE_KLINE_6H,
    "candle12H": MARKET_KLINE_KLINE_12H,
    "candle1D": MARKET_KLINE_KLINE_1D,
    "candle2D": MARKET_KLINE_KLINE_2D,
    "candle3D": MARKET_KLINE_KLINE_3D,
    "candle5D": MARKET_KLINE_KLINE_5D,
    "candle1W": MARKET_KLINE_KLINE_1W,
    "candle1M": MARKET_KLINE_KLINE_1M,
    "tickers": MARKET_TYPE_TICKER,
    "trades": MARKET_TYPE_TRADE,
    "books": MARKET_TYPE_ORDERBOOK,
}

OKX_CHANNEL_TRANSFORM = dict(zip(MARKET_CHANNEL_TRANSFORM.values(), MARKET_CHANNEL_TRANSFORM.keys()))


class OkxRestAPI:
    URI_CREATE_ORDER = "/api/v5/trade/order"
    URI_REVOKE_ORDER = "/api/v5/trade/cancel-order"
    URI_REVOKE_BATCH_ORDER = "/api/v5/trade/cancel-batch-orders"
    URI_AMEND_ORDER = "/api/v5/trade/amend-order"
    URI_ASSET_BALANCES = "/api/v5/asset/balances"
    URI_GET_ORDER_INFO = "/api/v5/trade/amend-order"
    URI_GET_PENDING_ORDER = "/api/v5/trade/orders-pending"
    URI_GET_POSITION = "/api/v5/account/positions"
    URI_SET_LEVERAGE = "/api/v5/account/set-leverage"

    def __init__(self, host, access_key, secret_key, passphrase, simulated=False):
        self._host = host
        self._access_key = access_key
        self._secret_key = secret_key
        self._passphrase = passphrase
        self._simulated = simulated

    async def request(self, method, uri, params=None, body=None, headers=None, auth=False):
        if params:
            query = "&".join(["{}={}".format(k, params[k]) for k in sorted(params.keys())])
            uri += "?" + query
        url = urljoin(self._host, uri)

        if auth:
            timestamp = str(time.time()).split(".")[0] + "." + str(time.time()).split(".")[1][:3]
            if body:
                body = json.dumps(body)
            else:
                body = ""
            message = str(timestamp) + str.upper(method) + uri + str(body)
            mac = hmac.new(bytes(self._secret_key, encoding="utf8"), bytes(message, encoding="utf-8"),
                           digestmod="sha256")
            d = mac.digest()
            sign = base64.b64encode(d)

            if not headers:
                headers = {}
            headers["Content-Type"] = "application/json"
            headers["OK-ACCESS-KEY"] = self._access_key.encode().decode()
            headers["OK-ACCESS-SIGN"] = sign.decode()
            headers["OK-ACCESS-TIMESTAMP"] = str(timestamp)
            headers["OK-ACCESS-PASSPHRASE"] = self._passphrase
            if self._simulated:
                headers["x-simulated-trading"] = "1"

        _, success, error = await AsyncHttpRequests.fetch(method, url, body=body, headers=headers, timeout=10)
        return success, error

    async def get_asset_balances(self):
        result, error = await self.request("GET", self.URI_ASSET_BALANCES, auth=True)
        return result, error

    async def set_level(self, symbol, position_side, lever, mgn_mode=ORDER_MARGIN_TYPE_CROSS):
        info = {
            "instId": symbol,
            "lever": str(lever),
            "mgn_mode": mgn_mode,
            "position_side": position_side
        }
        result, error = await self.request("POST", self.URI_SET_LEVERAGE, body=info, auth=True)
        return result, error

    async def create_order(self, symbol, action, price, quantity, order_type=ORDER_TYPE_LIMIT,
                           trade_mode=ORDER_NO_MARGIN_TYPE_CASH, inst_type=ORDER_INST_TYPE_SPOT):
        info = {
            "instId": symbol,
            "side": "buy" if action == ORDER_ACTION_BUY else "sell",
            "tdMode": "cash",
            "sz": quantity
        }
        if order_type == ORDER_TYPE_LIMIT:
            info["ordType"] = "limit"
            info["px"] = price
        elif order_type == ORDER_TYPE_MARKET:
            info["ordType"] = "market"
        else:
            logger.error("order_type error! order_type:", order_type, caller=self)
            return None, "order_type error!"

        if inst_type == ORDER_INST_TYPE_SPOT:
            info["tdMode"] = "cash"
            if action == ORDER_ACTION_BUY:
                info["side"] = "buy"
            elif action == ORDER_ACTION_SELL:
                info["side"] = "sell"
            else:
                logger.error("action error! action:", action, caller=self)
                return None, "action error!"
        elif inst_type in [ORDER_INST_TYPE_PERPETUAL, ORDER_INST_TYPE_MARGIN, ORDER_INST_TYPE_OPTIONS]:
            if trade_mode == ORDER_MARGIN_TYPE_ISOLATED:
                info["tdMode"] = "isolated"
            elif trade_mode == ORDER_MARGIN_TYPE_CROSS:
                info["tdMode"] = "cross"
            else:
                logger.error("trade_mode error! trade_mode:", trade_mode, caller=self)
                return None, "trade_mode error!"
            if action == ORDER_ACTION_BUY_LONG:
                info["side"] = "buy"
                info["posSide"] = "long"
            elif action == ORDER_ACTION_BUY_SHORT:
                info["side"] = "buy"
                info["posSide"] = "short"
            elif action == ORDER_ACTION_SELL_LONG:
                info["side"] = "sell"
                info["posSide"] = "long"
            elif action == ORDER_ACTION_SELL_SHORT:
                info["side"] = "sell"
                info["posSide"] = "short"
            else:
                logger.error("action error! action:", action, caller=self)
                return None, "action error!"
        else:
            logger.error("inst_type error! inst_type:", inst_type, caller=self)
            return None, "inst_type don't support"

        result, error = await self.request("POST", self.URI_CREATE_ORDER, body=info, auth=True)
        return result, error

    async def revoke_order(self, symbol, order_id):
        body = {
            "instId": symbol,
            "ordId": order_id
        }
        result, error = await self.request("POST", self.URI_REVOKE_ORDER, body=body, auth=True)
        return result, error

    async def revoke_orders(self, symbol, order_nos):
        if len(order_nos) > 20:
            logger.warn("only revoke 4 orders per request!", caller=self)
        body = [
            {
                "instrument_id": symbol,
                "order_ids": o
            } for o in order_nos[0:20]
        ]
        result, error = await self.request("POST", self.URI_REVOKE_ORDER, body=body, auth=True)
        return result, error

    async def get_order_status(self, symbol, order_no):
        params = {
            "instId": symbol,
            "ordId": order_no,
        }
        result, error = await self.request("GET", self.URI_GET_ORDER_INFO, params=params, auth=True)
        return result, error

    async def get_pending_order(self, symbol):
        params = {
            "instId": symbol
        }
        result, error = await self.request("GET", self.URI_GET_PENDING_ORDER, params=params, auth=True)
        return result, error

    async def get_current_pending_orders(self):
        result, error = await self.request("GET", self.URI_GET_PENDING_ORDER, params=None, auth=True)
        return result, error

    async def get_position(self, symbol):
        params = {
            "instId": symbol
        }
        result, error = await self.request("GET", self.URI_GET_POSITION, params=params, auth=True)
        return result, error

    async def get_current_positions(self):
        result, error = await self.request("GET", self.URI_GET_POSITION, params=None, auth=True)
        return result, error


class OkxTrade(WebSocket):

    def __init__(self, account, strategy, host=None, wss=None, access_key=None, secret_key=None, passphrase=None,
                 simulated=False, assets_update_callback=None, orders_update_callback=None,
                 position_update_callback=None):
        self._account = account
        self._strategy = strategy
        self._platform = OKX
        self._host = host if host else "https://www.okx.com"
        self._access_key = access_key
        self._secret_key = secret_key
        self._passphrase = passphrase
        self._simulated = simulated
        self._assets_update_callback = assets_update_callback
        self._orders_update_callback = orders_update_callback
        self._position_update_callback = position_update_callback
        if simulated:
            self._wss = wss if wss else "wss://wspap.okx.com:8443/ws/v5/private?brokerId=9999"
        else:
            self._wss = wss if wss else "wss://ws.okx.com:8443/ws/v5/private"

        super(OkxTrade, self).__init__(self._wss, send_hb_interval=5)
        self.heartbeat_msg = "ping"
        self._orders = {}
        self._assets = {}
        self._positions = {}
        self._rest_api = OkxRestAPI(self._host, self._access_key, self._secret_key, self._passphrase, self._simulated)
        self.initialize()

    @property
    def assets(self):
        return copy.copy(self._assets)

    @property
    def orders(self):
        return copy.copy(self._orders)

    @property
    def positions(self):
        return copy.copy(self._positions)

    async def connected_callback(self):
        timestamp = str(time.time()).split('.')[0] + '.' + str(time.time()).split('.')[1][:3]
        message = str(timestamp) + "GET" + "/users/self/verify"
        mac = hmac.new(bytes(self._secret_key, encoding="utf8"), bytes(message, encoding="utf8"), digestmod="sha256")
        d = mac.digest()
        signature = base64.b64encode(d).decode()
        data = {
            "op": "login",
            "args": [{
                "apiKey": self._access_key,
                "passphrase": self._passphrase,
                "timestamp": timestamp,
                "sign": signature
            }]
        }
        await self._ws.send_json(data)
        result, error = await self._rest_api.get_current_pending_orders()
        if error:
            logger.error("get current pending orders error", caller=self)
            return
        await self._update_orders(result.get("data"))

        result, error = await self._rest_api.get_current_positions()
        if error:
            logger.error("get current positions error", caller=self)
            return
        await self._update_positions(result.get("data"))

        result, error = await self._rest_api.get_asset_balances()
        if error:
            logger.error("get asset balances error", caller=self)
            return
        await self._update_asset_balances(result.get("data"))

    async def set_level(self, symbol, position_side, lever, mgn_mode):
        result, error = await self._rest_api.set_level(symbol, position_side, lever, mgn_mode)
        return result, error

    async def create_order(self, symbol, action, price, quantity, order_type=ORDER_TYPE_LIMIT,
                           trade_mode=ORDER_NO_MARGIN_TYPE_CASH, inst_type=ORDER_INST_TYPE_SPOT):
        price = str(price)
        quantity = str(quantity)
        result, error = await self._rest_api.create_order(symbol, action, price, quantity, order_type,
                                                          trade_mode, inst_type)
        if error:
            return None, error
        if result["data"][0]["sCode"] != "0":
            return None, result["data"][0]
        return result["data"][0]["ordId"], None

    async def revoke_order(self, symbol, order_id):
        result, error = await self._rest_api.revoke_order(symbol, order_id)
        if error:
            return None, error
        if result["data"][0]["sCode"] != "0":
            return None, result["data"][0]
        return result["data"][0]["ordId"], None

    async def _update_orders(self, orders):
        for order_info in orders:
            order_no = order_info["ordId"]
            state = order_info["state"]
            sz = 0 if order_info["sz"] == "" else float(order_info["sz"])
            fillSz = 0 if order_info["fillSz"] == "" else float(order_info["fillSz"])
            remain = sz - fillSz
            ctime = order_info["cTime"]
            utime = order_info["uTime"]
            instId = order_info["instId"]

            order = self._orders.get(order_no)
            if order:
                order.remain = remain
                order.status = state
                order.price = order_info["px"]
            else:
                info = {
                    "platform": self._platform,
                    "account": self._account,
                    "strategy": self._strategy,
                    "order_no": order_no,
                    "action": ORDER_ACTION_BUY if order_info["side"] == "buy" else ORDER_ACTION_SELL,
                    "symbol": instId,
                    "price": order_info["px"],
                    "quantity": order_info["sz"],
                    "remain": remain,
                    "status": state,
                    "avg_price": order_info["px"]
                }
                order = Order(**info)
                self._orders[order_no] = order
            order.ctime = ctime
            order.utime = utime
            if state in [ORDER_STATUS_FAILED, ORDER_STATUS_CANCELED, ORDER_STATUS_FILLED]:
                self._orders.pop(order_no)
        if self._orders_update_callback:
            SingleTask.run(self._orders_update_callback, self._orders)

    async def _update_positions(self, positions):
        for position_info in positions:
            posId = position_info["posId"]
            utime = position_info["utime"]
            instId = position_info["instId"]
            position_side = position_info["posSide"]
            pos = position_info["pos"]
            avail_position = position_info["availPos"]
            position = self._positions.get(posId)
            if position:
                position.platform = self._platform
                position.account = self._account
                position.strategy = self._strategy
                position.symbol = instId
                position.position_side = position_side
                position.pos = pos
                position.avail_position = avail_position
                position.utime = utime
            else:
                info = {
                    "platform": self._platform,
                    "account": self._account,
                    "strategy": self._strategy,
                    "pos_id": posId,
                    "position_side": position_side,
                    "pos": pos,
                    "avail_position": avail_position,
                    "utime": utime
                }
                position = Position(**info)
                self._positions[posId] = position
        if self._orders_update_callback:
            SingleTask.run(self._orders_update_callback, self._positions)

    async def _update_asset_balances(self, data):
        if len(data) <= 0:
            return
        assets = data[0]['details']
        for a in assets:
            asset = self._assets.get("ccy")
            if asset:
                asset.avail = float(a["cashBal"]) - float(a["frozenBal"])
                asset.total = float(a["cashBal"])
                asset.frozen = float(a["frozenBal"])
            else:
                info = {
                    "avail": float(a["cashBal"]) - float(a["frozenBal"]),
                    "total": float(a["cashBal"]),
                    "frozen": float(a["frozenBal"]),
                }
                self._assets[a["ccy"]] = info
        if self._assets_update_callback:
            SingleTask.run(self._assets_update_callback, self._assets)

    async def process(self, msg):
        if msg == "pong":  # 心跳返回
            return
        try:
            data = json.loads(msg)
        except:
            data = msg.data
        event = data.get("event")
        if event:
            if event == "login":
                logger.info("Websocket connection authorized successfully.", caller=self)
                # subscribe all order info
                data = {
                    "op": "subscribe",
                    "args": [{
                        "channel": "orders",
                        "instType": "ANY"
                    }, {
                        "channel": "account"
                    }, {
                        "channel": "positions",
                        "instType": "ANY"
                    }]
                }
                await self._ws.send_json(data)
                logger.info("subscribe orders,account,positions successfully.", caller=self)
                return
            elif event == "subscribe":
                return
            elif event == "error":
                logger.error("event:", event, "code", data.get("code"),
                             data.get("msg"), caller=self)
                return
        chanel = data.get("arg").get("channel")
        if chanel == "orders":
            await self._update_orders(data["data"])
        elif chanel == "positions":
            await self._update_positions(data["data"])
        elif chanel == "account":
            await self._update_asset_balances(data["data"])
        else:
            logger.warn("not support message:", data)


class OkxMarket(WebSocket):
    def __init__(self, wss=None, simulated=False, subscribes=None):
        self._platform = OKX
        self._subscribes = subscribes
        self._simulate = simulated
        self._wss = wss
        self.heartbeat_msg = "ping"
        super(OkxMarket, self).__init__(self._wss)
        # self.initialize()

    def load_configs(self):
        market_config = config.platforms.get(self._platform).get("market")
        if market_config is None:
            logger.error("config file error!")
            exit(0)
        self._simulate = config.platforms.get(self._platform).get("simulate", False)
        self._subscribes = list(market_config.get("subscribes"))
        if self._simulate:
            self._wss = market_config.get("wss", "wss://wspap.okx.com:8443/ws/v5/public?brokerId=999")
        else:
            self._wss = market_config.get("wss", "wss://ws.okx.com:8443/ws/v5/public")
        super(OkxMarket, self).__init__(self._wss)
        return self

    async def connected_callback(self):
        ches = []
        for sub in self._subscribes:
            symbols = list(sub.get("symbols"))
            channels = list(sub.get("channels"))
            for channel in channels:
                if channel not in OKX_CHANNEL_TRANSFORM:
                    logger.error("don't support subscribe channel type:", channel, caller=self)
                    continue
                for symbol in symbols:
                    info = {
                        "channel": OKX_CHANNEL_TRANSFORM[channel],
                        "instId": symbol
                    }
                    ches.append(info)
        if ches:
            msg = {
                "op": "subscribe",
                "args": ches
            }
            logger.debug("subscribe msg:", msg, caller=self)
            await self._ws.send_json(msg)
            logger.info("subscribe channels success.", caller=self)

    async def process(self, msg):
        try:
            data = json.loads(msg)
        except:
            data = msg.data
        if data == "pong":  # 心跳返回
            return
        event = data.get("event")
        if event:
            if event == "subscribe":
                return
            elif event == "error":
                logger.error("event:", event, "code", data.get("code"),
                             data.get("msg"), caller=self)
                return

        chanel = data.get("arg").get("channel")
        if chanel.startswith("candle"):
            await self.deal_kline_update(data)
        elif chanel == "trades":
            await self.deal_trade_update(data)
        elif chanel == "books":
            await self.deal_books_update(data)
        elif chanel == "tickers":
            await self.deal_ticker_update(data)
        else:
            logger.warn("not support message:", data)

    async def deal_ticker_update(self, msg):
        symbol = msg.get("arg").get("instId")
        datas = msg.get("data")
        for data in datas:
            d = {
                "platform": self._platform,
                "symbol": symbol,
                "last_price": data.get("last"),
                "last_size": data.get("lastSz"),
                "ask_price": data.get("askPx"),
                "ask_size": data.get("askSz"),
                "bid_price": data.get("bidPx"),
                "bid_size": data.get("bidSz"),
                "timestamp": data.get("ts")
            }
            EventTicker(Ticker(**d)).publish()
        logger.info("symbol:", symbol, "ticker", datas, caller=self)

    async def deal_kline_update(self, msg):
        symbol = msg.get("arg").get("instId")
        channel = msg.get("arg").get("channel")
        data = msg.get("data")

        if channel not in MARKET_CHANNEL_TRANSFORM:
            logger.error("don't support kline type:", channel, caller=self)
            return

        d = {
            "platform": self._platform,
            "timestamp": int(data[0][0]),
            "symbol": symbol,
            "open": float(data[0][1]),
            "high": float(data[0][2]),
            "low": float(data[0][3]),
            "close": float(data[0][4]),
            "volume": float(data[0][5]),
            "kline_type": MARKET_CHANNEL_TRANSFORM[channel]
        }

        EventKline(Kline(**d)).publish()
        logger.info("symbol:", symbol, "kline", d, caller=self)

    async def deal_trade_update(self, msg):
        symbol = msg.get("arg").get("instId")
        datas = msg.get("data")
        for data in datas:
            d = {
                "platform": self._platform,
                "symbol": symbol,
                "action": data.get("side"),
                "price": data.get("px"),
                "quantity": data.get("sz"),
                "timestamp": data.get("ts")
            }
            EventTrade(Trade(**d)).publish()
        logger.info("symbol:", symbol, "trade", datas, caller=self)

    async def deal_books_update(self, msg):
        symbol = msg.get("arg").get("instId")
        datas = msg.get("data")
        for data in datas:
            d = {
                "platform": self._platform,
                "symbol": symbol,
                "asks": data.get("asks"),
                "bids": data.get("bids"),
                "timestamp": data.get("ts")
            }
            EventOrderbook(Orderbook(**d)).publish()
        logger.info("symbol:", symbol, "trade", datas, caller=self)
