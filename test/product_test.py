from anquant import quant
from anquant.config import config
from anquant.constant import OKX
from anquant.platform.okx import OkxMarket
from anquant.utils import logger

# def load_market(platform):
#     if platform == OKX:
#         market_config = config.platforms.get(platform).get("market")
#         if market_config is None:
#             logger.error("config file error!")
#             exit(0)
#         wss = market_config.get("wss", "wss://wspap.okx.com:8443/ws/v5/public?brokerId=999")
#         simulate = config.platforms.get(platform).get("simulate", False)
#         subscribes = list(market_config.get("subscribes"))
#         OkxMarket(platform, wss, simulate, subscribes).initialize()


if __name__ == '__main__':
    quant.initialize("./config.json")
    OkxMarket(OKX).load_configs().initialize()
    quant.start()
