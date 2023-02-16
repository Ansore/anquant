# -*- coding:utf-8 -*-
from anquant.market import Kline
from anquant.utils.mongo import MongoCollection


class KlineStorage(MongoCollection):

    def __init__(self, platform):
        self._db_name = platform
        self._current_timestamp = 0
        self._collection_name = "kline"
        print(self._db_name)
        super(KlineStorage, self).__init__(self._db_name, self._collection_name)

    async def save_kline(self, kline: Kline):
        if self._current_timestamp >= int(kline.timestamp):
            return
        self._current_timestamp = int(kline.timestamp)
        r_id = kline.symbol + "_" + kline.kline_type + "_" + str(kline.timestamp)
        await self.save_or_update_one(r_id, kline.data)
