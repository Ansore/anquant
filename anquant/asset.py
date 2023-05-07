# -*- coding:utf-8 -*-
import json


class Asset:

    def __init__(self, platform=None, account=None, assets=None, timestamp=None, update=False):
        self.platform = platform
        self.account = account
        self.assets = assets
        self.timestamp = timestamp
        self.update = update

    @property
    def data(self):
        d = {
            "platform": self.platform,
            "account": self.account,
            "assets": self.assets,
            "timestamp": self.timestamp,
            "update": self.update
        }
        return d

    def __str__(self):
        info = json.dumps(self.data)
        return info

    def __repr__(self):
        return str(self)


class AssetSubscribe:

    def __init__(self, platform, account, callback):
        """ Initialize. """
        if platform == "#" or account == "#":
            multi = True
        else:
            multi = False
        from anquant.event import EventAsset
        EventAsset(Asset(platform, account)).subscribe(callback, multi)
