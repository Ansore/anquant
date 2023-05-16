from anquant import quant, constant
from anquant.constant import OKX
from anquant.market import Market, Kline
from anquant.order import ORDER_ACTION_BUY, ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET, ORDER_ACTION_SELL
from anquant.platform.okx import OkxMarket
from anquant.tasks import SingleTask, LoopTask
from anquant.trade import Trade
from anquant.config import Config


class MyStrategy:

    def __init__(self, config):
        """ 初始化
        """
        self.strategy = "my_strategy"
        self.platform = OKX
        self.simulated = True
        self.account = config.platforms.get(self.platform, {}).get("account")
        self.access_key = self.account.get("access_key")
        self.secret_key = self.account.get("secret_key")
        self.passphrase = self.account.get("passphrase")
        self.trade = Trade(platform=self.platform, strategy=self.strategy, account=self.account,
                           assets_update_callback=self.assets_update_callback,
                           orders_update_callback=self.orders_update_callback,
                           position_update_callback=self.position_update_callback)
        # SingleTask.call_later(self.buy_order, 5)
        # SingleTask.call_later(self.sell_order, 5)
        # SingleTask.call_later(self.display_info, 3)
        # LoopTask.register(self.display_info, 3)

    async def orders_update_callback(self, orders):
        print("orders_update_callback", orders)
        # pass

    async def assets_update_callback(self, assets):
        print("assets_update_callback", assets)

    async def position_update_callback(self, positions):
        print("position_update_callback", positions)
        # pass

    async def display_info(self, *args, **kwargs):
        print("----------display_info------orders")
        print(self.trade.orders)
        print("----------display_info------positions")
        print(self.trade.positions)
        print("----------display_info------end")

    async def sell_order(self):
        # order_id, error = await self.trade.create_order("BAL-USDT", ORDER_ACTION_SELL, 52, 3.2, ORDER_TYPE_MARKET)
        order_id, error = await self.trade.create_order("BTC-USDT", ORDER_ACTION_SELL, 52, 1, ORDER_TYPE_MARKET)
        if error:
            print("----revoke_o error, ", error)
            return
        print("#######testStrategy----sell order success")

    async def buy_order(self):
        print("******testStrategy")
        # order_id, error = await self.trade.create_order("BAL-USDT", ORDER_ACTION_BUY, 52, 10, ORDER_TYPE_MARKET)
        order_id, error = await self.trade.create_order("BTC-USDT", ORDER_ACTION_BUY, 27700, 1.13, ORDER_TYPE_MARKET)
        if error:
            print("----testStrategy create_order error, ", error)
            return
        print(order_id)
        print("#######testStrategy----create order success")
        SingleTask.call_later(self.sell_order, 25)
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
    config = Config("./config.json")
    quant.initialize(config)
    MyStrategy(config)
    # consume()
    quant.start()
