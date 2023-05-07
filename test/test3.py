from anquant import quant
from anquant.config import config
from anquant.constant import OKX
from anquant.order import ORDER_ACTION_BUY, ORDER_POSITION_SIDE_LONG, ORDER_MARGIN_TYPE_CROSS, ORDER_ACTION_BUY_LONG, \
    ORDER_INST_TYPE_PERPETUAL
from anquant.tasks import SingleTask
from anquant.trade import Trade


class MyStrategy:

    def __init__(self):
        """ 初始化
        """
        self.strategy = "my_strategy"
        self.platform = OKX
        self.simulated = True
        self.symbol = "BTC-USDT-SWAP"
        self.account = config.platforms.get(self.platform, {}).get("account")
        self.access_key = self.account.get("access_key")
        self.secret_key = self.account.get("secret_key")
        self.passphrase = self.account.get("passphrase")
        self.name = config.strategy
        self.trade = Trade(strategy=self.strategy, platform=self.platform, access_key=self.access_key,
                           secret_key=self.secret_key, passphrase=self.passphrase, simulated=self.simulated,
                           assets_update_callback=self.assets_update_callback,
                           orders_update_callback=self.orders_update_callback,
                           position_update_callback=self.position_update_callback,
                           )
        SingleTask.call_later(self.testStrategy, 5)

    async def orders_update_callback(self, orders):
        print("orders_update_callback", orders)
        # pass

    async def position_update_callback(self, positions):
        print("position_update_callback", positions)
        # pass

    async def assets_update_callback(self, assets):
        print("assets_update_callback", assets)

    async def revoke_o(self, orderId):
        print("****** revoke order start ********")
        print("revoke_order: ", orderId)
        order_id, error = await self.trade.revoke_order(self.symbol, orderId)
        if error:
            print("----revoke_o error, ", error)
        print("****** revoke order end ********")

    async def testStrategy(self):
        print("****** set level start ********")
        await self.trade.set_level(self.symbol, ORDER_POSITION_SIDE_LONG, 10, ORDER_MARGIN_TYPE_CROSS)

        print("****** set level end ********")
        print("****** create order start ********")
        order_id, error = await self.trade.create_order(self.symbol, ORDER_ACTION_BUY_LONG, 16000, 1,
                                      trade_mode=ORDER_MARGIN_TYPE_CROSS,
                                      inst_type=ORDER_INST_TYPE_PERPETUAL)
        if error:
            print("create order error", error)
            return
        print("****** create order end ********")
        SingleTask.call_later(self.revoke_o, 5, order_id)


if __name__ == '__main__':
    quant.initialize("./config.json")
    MyStrategy()
    quant.start()
