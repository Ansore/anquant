# -*- coding:utf-8 -*-
import asyncio

from anquant.config import config
from anquant.utils import logger
from anquant.utils import tools

__all__ = ("heartbeat",)


class HeartBeat:
    def __init__(self):
        self._count = 0
        self._interval = 1
        self._print_interval = 0
        self._broadcast_interval = 0
        self._tasks = {}

    @property
    def count(self):
        return self._count

    def load_configs(self):
        self._interval = config.heartbeat.get("interval", 1)
        self._print_interval = config.heartbeat.get("print_interval", 0)
        self._broadcast_interval = config.heartbeat.get("broadcast", 0)

    def ticker(self):
        self._count += 1
        if self._print_interval > 0 and self._count % self._print_interval == 0:
            logger.info("server heart, count:", self._count, caller=self)

        # setting next heart
        asyncio.get_event_loop().call_later(self._interval, self.ticker)

        # task callback
        for task in self._tasks.values():
            interval = task["interval"]
            if self._count % interval != 0:
                continue
            func = task["func"]
            args = task["args"]
            kwargs = task["kwargs"]
            kwargs["heart_beat_count"] = self._count
            asyncio.get_event_loop().create_task(func(*args, **kwargs))

        if self._broadcast_interval > 0 and self._count % self._broadcast_interval == 0:
            self.alive()

    def register(self, func,  interval=1, *args, **kwargs):
        """
        register a task
        :param func:
        :param interval:
        :param args:
        :param kwargs:
        :return:
        """
        task_id = tools.get_uuid1()
        self._tasks[task_id] = {
            "func": func,
            "interval": interval,
            "args": args,
            "kwargs": kwargs
        }
        return task_id

    def unregister(self, task_id):
        """
        unresigter a task
        :param task_id:
        :return:
        """
        if task_id in self._tasks:
            self._tasks.pop(task_id)

    def alive(self):
        """
        broadcast heart
        :return:
        """
        from anquant.event import EventHeartbeat
        EventHeartbeat(config.server_id, self.count).publish()


heartbeat = HeartBeat()
