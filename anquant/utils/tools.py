# -*- coding:utf-8 -*-
import datetime
import uuid
import time


def get_cur_timestamp():
    """Get current timestamp of second"""
    return int(time.time())


def get_cur_timestamp_ms():
    """Get current timestamp of millisecond"""
    return int(time.time() * 1000)


def get_datetime_str(fmt="%Y-%m-%d %H:%M:%S"):
    """
    get date time string
    :param fmt: date format
    :return: string of date time
    """
    return datetime.datetime.today().strftime(fmt)


def utctime_str_to_mts(utctime_str, fmt="%Y-%m-%dT%H:%M:%S.%fZ"):
    """ 将UTC日期时间格式字符串转换成时间戳（毫秒）
    @param utctime_str 日期时间字符串 eg: 2019-03-04T09:14:27.806Z
    @param fmt 日期时间字符串格式
    @return timestamp 时间戳(毫秒)
    """
    dt = datetime.datetime.strptime(utctime_str, fmt)
    timestamp = int(dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None).timestamp() * 1000)
    return timestamp


def get_uuid1():
    """
    make a uuid based on the host ID and current time
    :return:
    """
    return str(uuid.uuid1())
