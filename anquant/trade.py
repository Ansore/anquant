# -*- coding:utf-8 -*-
from anquant.constant import OKX
from anquant.order import ORDER_TYPE_LIMIT, ORDER_NO_MARGIN_TYPE_CASH, ORDER_INST_TYPE_SPOT
from anquant.platform.okx import OkxTrade


class Trade:
    def __init__(self, strategy, account, platform=OKX, host=None, wss=None, assets_update_callback=None,
                 orders_update_callback=None, position_update_callback=None, **kwargs):
        self._platform = platform
        self._strategy = strategy

        if platform == OKX:
            self._t = OkxTrade(strategy, account, host, wss, assets_update_callback=assets_update_callback,
                               orders_update_callback=orders_update_callback,
                               position_update_callback=position_update_callback)

    @property
    def assets(self):
        return self._t.assets

    @property
    def positions(self):
        return self._t.positions

    @property
    def orders(self):
        return self._t.orders

    async def set_level(self, symbol, position_side, lever, mgn_mode):
        """
        设置杠杆
        :param symbol: 交易对
        :param position_side: 持仓方向 long双向持仓多头  short双向持仓空头
        :param lever: 杠杆倍数
        :param mgn_mode: 保证金模式 isolated：逐仓 cross：全仓
        :return:
        """
        result, error = await self._t.set_level(symbol, position_side, lever, mgn_mode)
        return result, error

    async def create_order(self, symbol, action, price, quantity, order_type=ORDER_TYPE_LIMIT,
                           trade_mode=ORDER_NO_MARGIN_TYPE_CASH, inst_type=ORDER_INST_TYPE_SPOT):
        """
        创建订单
        :param symbol: 交易对
        :param action:
        :param price: 价格
        :param quantity: 数量
        :param order_type: 市价/限价
        :param trade_mode: 非保证金/逐仓/全仓
        :param inst_type: 交易对类型:现货/永续/期货
        :return: 订单号
        """
        order_no, error = await self._t.create_order(symbol, action, price, quantity, order_type,
                                                     trade_mode, inst_type)
        return order_no, error

    async def revoke_order(self, symbol, order_id):
        order_no, error = await self._t.revoke_order(symbol, order_id)
        return order_no, error

    async def get_pending_order(self, symbol):
        raise NotImplementedError
