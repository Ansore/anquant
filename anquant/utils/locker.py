# -*- coding:utf-8 -*-
import asyncio
import functools

METHOD_LOCKERS = {}


def async_method_locker(name, wait=True):
    """
    async add locker
    :param name:
    :param wait:
    :return:
    """
    assert isinstance(name, str)

    def decorating_function(method):
        global METHOD_LOCKERS
        locker = METHOD_LOCKERS.get(name)
        if not locker:
            locker = asyncio.Lock()
            METHOD_LOCKERS[name] = locker

        @functools.wraps(method)
        async def wrapper(*args, **kwargs):
            if not wait and locker.locked():
                return
            try:
                await locker.acquire()
                return await method(*args, **kwargs)
            finally:
                locker.release()
        return wrapper
    return decorating_function