from anquant import quant, constant
from anquant.config import config
from anquant.constant import OKX
from anquant.market import Market, Kline
from anquant.order import ORDER_ACTION_BUY, ORDER_TYPE_LIMIT
from anquant.platform.okx import OkxMarket
from anquant.tasks import SingleTask, LoopTask
from anquant.trade import Trade


class MyStrategy:

    def __init__(self):
        """ 初始化
        """
        self.strategy = "my_strategy"
        self.platform = OKX
        self.simulated = True
        self.account = config.platforms.get(self.platform, {}).get("account")
        self.access_key = self.account.get("access_key")
        self.secret_key = self.account.get("secret_key")
        self.passphrase = self.account.get("passphrase")
        self.name = config.strategy
        self.trade = Trade(strategy=self.strategy, platform=self.platform, access_key=self.access_key,
                           secret_key=self.secret_key, passphrase=self.passphrase, simulated=self.simulated,
                           orders_update_callback=self.orders_update_callback,
                           position_update_callback=self.position_update_callback)
        SingleTask.call_later(self.testStrategy, 5)
        # SingleTask.call_later(self.display_info, 3)
        LoopTask.register(self.display_info, 3)

    async def orders_update_callback(self, orders):
        print("orders_update_callback", orders)
        # pass

    async def position_update_callback(self, positions):
        print("position_update_callback", positions)
        # pass

    async def display_info(self, *args, **kwargs):
        print("----------display_info------orders")
        print(self.trade.orders)
        print("----------display_info------positions")
        print(self.trade.positions)
        print("----------display_info------assets")
        print(self.trade.assets)
        print("----------display_info------end")

    async def revoke_o(self, orderId):
        print(orderId)
        order_id, error = await self.trade.revoke_order("BTC-USDT", orderId)
        if error:
            print("----revoke_o error, ", error)
        print("#######testStrategy----revoke_o order success")

    async def testStrategy(self):
        print("******testStrategy")
        order_id, error = await self.trade.create_order("BTC-USDT", ORDER_ACTION_BUY, 19000, 1, ORDER_TYPE_LIMIT)
        if error:
            print("----testStrategy create_order error, ", error)
            return

        print(order_id)
        print("#######testStrategy----create order success")
        SingleTask.call_later(self.revoke_o, 5, order_id)
        print("#######testStrategy")


def consume():
    async def callback(k: Kline):
        print("platform", k.platform)
        print("symbol", k.symbol)
        print("open", k.open)
        print("high", k.high)
        print("low", k.low)
        print("close", k.close)
    Market(constant.MARKET_TYPE_KLINE, constant.OKX, "BTC-USDT", callback)


if __name__ == '__main__':
    quant.initialize("./config.json")
    MyStrategy()
    quant.start()
