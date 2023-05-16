# -*- coding:utf-8 -*-
from anquant.utils import tools

ORDER_TYPE_LIMIT = "LIMIT"
ORDER_TYPE_MARKET = "MARKET"

ORDER_NO_MARGIN_TYPE_CASH = "cash"
ORDER_MARGIN_TYPE_ISOLATED = "isolated"
ORDER_MARGIN_TYPE_CROSS = "cross"

ORDER_INST_TYPE_SPOT = "spot"
ORDER_INST_TYPE_SWAP = "swap"
ORDER_INST_TYPE_FUTURES = "futures"
ORDER_INST_TYPE_MARGIN = "margin"
ORDER_INST_TYPE_OPTIONS = "options"

ORDER_ACTION_BUY = "BUY"
ORDER_ACTION_SELL = "SELL"
ORDER_ACTION_BUY_LONG = "BUY_LONG"  # 开多
ORDER_ACTION_SELL_LONG = "SELL_LONG"  # 平多
ORDER_ACTION_BUY_SHORT = "BUY_SHOR"  # 开空
ORDER_ACTION_SELL_SHORT = "SELL_SHOR"  # 平空

ORDER_POSITION_SIDE_LONG = "long"
ORDER_POSITION_SIDE_SHORT = "short"

# 订单状态
ORDER_STATUS_NONE = "none"
ORDER_STATUS_SUBMITTED = "live"
ORDER_STATUS_PARTIAL_FILLED = "partially_filled"
ORDER_STATUS_FILLED = "filled"
ORDER_STATUS_CANCELED = "canceled"
ORDER_STATUS_FAILED = "failed"

TRADE_TYPE_NONE = 0
TRADE_TYPE_BUY_OPEN = 1
TRADE_TYPE_SELL_OPEN = 2
TRADE_TYPE_SELL_CLOSE = 3
TRADE_TYPE_BUY_CLOSE = 4


class Order:
    def __init__(self, account=None, platform=None, strategy=None, order_no=None, symbol=None, action=None, price=0,
                 quantity=0, remain=0, status=ORDER_STATUS_NONE, avg_price=0, order_type=ORDER_TYPE_LIMIT,
                 trade_type=TRADE_TYPE_NONE, ctime=None, utime=None):
        self.platform = platform
        self.account = account
        self.strategy = strategy
        self.order_no = order_no
        self.action = action
        self.order_type = order_type
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
        self.remain = remain
        self.status = status
        self.avg_price = avg_price
        self.trade_type = trade_type
        self.ctime = ctime if ctime else tools.get_cur_timestamp()
        self.utime = utime if utime else tools.get_cur_timestamp()

    def __str__(self):
        info = "[platform: {platform}, account: {account}, strategy: {strategy}, order_no: {order_no}, " \
               "action: {action}, symbol: {symbol}, price: {price}, quantity: {quantity}, remain: {remain}, " \
               "status: {status}, avg_price: {avg_price}, order_type: {order_type}, trade_type: {trade_type}, " \
               "ctime: {ctime}, utime: {utime}]".format(
                platform=self.platform, account=self.account, strategy=self.strategy, order_no=self.order_no,
                action=self.action, symbol=self.symbol, price=self.price, quantity=self.quantity,
                remain=self.remain, status=self.status, avg_price=self.avg_price, order_type=self.order_type,
                trade_type=self.trade_type, ctime=self.ctime, utime=self.utime)
        return info

    def __repr__(self):
        return str(self)
