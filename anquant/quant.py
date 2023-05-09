# -*- coding:utf-8 -*-
import asyncio

from anquant.utils import logger


class Anquant:
    def __init__(self):
        self.loop = None
        self.event_engine = None
        self.config = None

    def initialize(self, config):
        self.config = config
        self._get_event_loop()
        self._init_logger()
        self._init_event_engine()
        self._do_heartbeat()

    def start(self):
        logger.info("start io loop ...", caller=self)
        self.loop.run_forever()

    def stop(self):
        logger.info("stop io loop.", caller=self)
        # TODO: clean up running coroutine
        self.loop.stop()

    def _get_event_loop(self):
        if not self.loop:
            self.loop = asyncio.get_event_loop()
        return self.loop

    def _init_logger(self):
        console = self.config.log.get("console", True)
        level = self.config.log.get("level", "DEBUG")
        path = self.config.log.get("path", "/tmp/logs/quant")
        name = self.config.log.get("name", "quant.log")
        clear = self.config.log.get("clear", False)
        backup_count = self.config.log.get("backup_count", 0)
        if console:
            logger.init_logger(level)
        else:
            logger.init_logger(level, path, name, clear, backup_count)

    def _init_event_engine(self):
        if self.config.rabbitmq:
            from anquant.event_engine import EventEngine
            self.event_engine = EventEngine(self.config.rabbitmq)
            # config.initialize()

    def _do_heartbeat(self):
        from anquant.heartbeat import heartbeat
        heartbeat.load_configs(self.config.server_id, self.config.heartbeat)
        self.loop.call_later(0.5, heartbeat.ticker)
