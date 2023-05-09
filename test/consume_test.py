from anquant import quant, constant
from anquant.constant import OKX
from anquant.data import KlineStorage
from anquant.market import Market, Kline, Trade, Orderbook
from anquant.utils.mongo import initMongoDB
from anquant.config import Config


def consume():
    initMongoDB("91.151.93.110", 27017, "ansore", "ansore")
    ks = KlineStorage(OKX)

    async def callback(k: Kline):
        print(k)
        # print("save kline:", k.symbol, "-", str(k.timestamp), "-", str(k.high))
        # await ks.save_kline(k)

    Market(constant.MARKET_TYPE_KLINE, OKX, "BTC-USDT", callback)

    # async def callback_trade(t: Trade):
    #     print("platform:", t.platform, "symbol:", t.symbol, "action:", t.action,
    #           "price", t.price, "quantity:", t.quantity, "timestamp:", t.timestamp)
    # Market(constant.MARKET_TYPE_TRADE, constant.OKX, "BTC-USDT", callback_trade)

    # async def callback_Orderbook(o: Orderbook):
    #     print("platform:", o.platform)
    # Market(constant.MARKET_TYPE_ORDERBOOK, constant.OKX, "BTC-USDT", callback_Orderbook)


if __name__ == '__main__':
    config = Config()
    config.loads("./config.json")
    quant.initialize(config)
    consume()
    quant.start()
