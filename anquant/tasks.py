# -*- coding:utf-8 -*-
import asyncio
import inspect

from anquant.heartbeat import heartbeat


class LoopTask:
    @classmethod
    def register(cls, func, interval=1, *args, **kwargs):
        """
        register a loop task
        execute on heart
        :param func: execute function, must is async
        :param interval: second
        :param args:
        :param kwargs:
        :return: task id
        """
        return heartbeat.register(func, interval, *args, **kwargs)

    @classmethod
    def unregister(cls, task_id):
        """
        unregister a loop task
        :param task_id:
        :return:
        """
        heartbeat.unregister(task_id)


class SingleTask:
    @classmethod
    def run(cls, func, *args, **kwargs):
        """
        run a function
        :param func:
        :param args:
        :param kwargs:
        :return:
        """
        asyncio.get_event_loop().create_task(func(*args, **kwargs))

    @classmethod
    def call_later(cls, func, delay=0, *args, **kwargs):
        """
        call a function later
        :param delay:
        :param func:
        :param args:
        :param kwargs:
        :return:
        """
        if not inspect.iscoroutinefunction(func):
            asyncio.get_event_loop().call_later(delay, func, *args)
        else:
            def foo(f, *args, **kwargs):
                asyncio.get_event_loop().create_task(f(*args, **kwargs))
            asyncio.get_event_loop().call_later(delay, foo, func, *args)
