# -*- coding:utf-8 -*-

from anquant.utils import tools


POSITION_SIDE_LONG = "long"
POSITION_SIDE_SHORT = "short"
POSITION_SIDE_NET = "net"


class Position:
    def __init__(self, platform=None, account=None, strategy=None, symbol=None, pos_id=None, position_side=None,
                 pos=None, avail_position=None, utime=None):
        self.platform = platform
        self.account = account
        self.strategy = strategy
        self.symbol = symbol
        self.pos_id = pos_id
        self.position_side = position_side
        self.pos = pos
        self.avail_position = avail_position
        self.utime = utime

    def update(self, position_side=0, pos=0, avail_position=0, utime=None):
        self.position_side = position_side
        self.pos = pos
        self.avail_position = avail_position
        self.utime = utime if utime else tools.get_cur_timestamp_ms()

    def __str__(self):
        info = "[platform: {platform}, account: {account}, strategy: {strategy}, symbol: {symbol}, " \
               "position_side: {position_side}, pos: {pos}, " \
               "avail_position: {avail_position}, utime: {utime}]"\
            .format(platform=self.platform, account=self.account, strategy=self.strategy, symbol=self.symbol,
                    position_side=self.position_side, pos=self.pos,
                    avail_position=self.avail_position, utime=self.utime)
        return info

    def __repr__(self):
        return str(self)
