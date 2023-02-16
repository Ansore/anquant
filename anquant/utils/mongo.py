# -*- coding:utf-8 -*-
import asyncio

import pymongo
from urllib.parse import quote_plus

mongo_client = None


def initMongoDB(host="127.0.0.1", port=27017, username="", password="", dbname="admin"):
    global mongo_client
    username = quote_plus(username)
    password = quote_plus(password)
    mongo_client = pymongo.MongoClient('mongodb://%s:%s@%s:%d/%s' % (username, password, host, port, dbname))


class MongoCollection:
    def __init__(self, db_name, collection_name):
        self._db_name = db_name
        self._collection_name = collection_name
        self._conn = mongo_client
        self._db = self._conn[db_name]
        self._cursor = self._conn[db_name][collection_name]

    async def get_list(self, spec=None, fields=None, sort=None, skip=0, limit=99999, cursor=None):
        if fields is None:
            fields = {}
        if spec is None:
            spec = {}
        if cursor is None:
            cursor = self._cursor
        r = cursor.find(spec, fields)
        if sort is not None:
            r.sort(sort)
        return r.limit(limit).skip(skip)

    async def find_one(self, spec=None, fields=None, sort=None, skip=0, cursor=None):
        if fields is None:
            fields = {}
        if spec is None:
            spec = {}
        return await self.get_list(spec, fields, sort, skip, 1, cursor)

    async def save_or_update_one(self, r_id, row, cursor=None):
        if cursor is None:
            cursor = self._cursor
        cursor.update_one({"_id": r_id}, {"$set": row}, upsert=True)

    async def count(self, spec=None, cursor=None):
        if spec is None:
            spec = {}
        if cursor is None:
            cursor = self._cursor
        return len(list(cursor.find(spec)))


# async def test():
#     c = MongoCollection("stock", "hs300")
#     li = await c.get_list()
#     print(list(li))
#     c = MongoCollection("stock", "zz500")
#     li = await c.get_list()
#     print(list(li))
#     print(list(await c.find_one({"_id": "sh.600008"}, {"_id": 0, "code": 1})))
#     print(await c.count())
#     c = MongoCollection("test", "tst")
#     await c.save_or_update_one("123123", {"123": "345"})
#
#
# if __name__ == '__main__':
#     initMongoDB("localhost", 27017, "admin", "admin")
#     asyncio.new_event_loop().run_until_complete(test())
