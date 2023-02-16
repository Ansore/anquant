# -*- coding:utf-8 -*-
from anquant.constant import OKX
from anquant.order import ORDER_TYPE_LIMIT, ORDER_NO_MARGIN_TYPE_CASH, ORDER_INST_TYPE_SPOT
from anquant.platform.okx import OkxTrade


class Trade:
    def __init__(self, strategy, platform, host=None, wss=None, account=None, access_key=None, secret_key=None,
                 passphrase=None, simulated=False, assets_update_callback=None, orders_update_callback=None,
                 position_update_callback=None, **kwargs):
        self._platform = platform
        self._strategy = strategy

        if platform == OKX:
            self._t = OkxTrade(account, strategy, host, wss, access_key, secret_key, passphrase, simulated,
                               assets_update_callback=assets_update_callback,
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
        result, error = await self._t.set_level(symbol, position_side, lever, mgn_mode)
        return result, error

    async def create_order(self, symbol, action, price, quantity, order_type=ORDER_TYPE_LIMIT,
                           trade_mode=ORDER_NO_MARGIN_TYPE_CASH, inst_type=ORDER_INST_TYPE_SPOT):
        order_no, error = await self._t.create_order(symbol, action, price, quantity, order_type,
                                                     trade_mode, inst_type)
        return order_no, error

    async def revoke_order(self, symbol, order_id):
        order_no, error = await self._t.revoke_order(symbol, order_id)
        return order_no, error

    async def get_pending_order(self, symbol):
        raise NotImplementedError
