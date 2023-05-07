# -*- coding:utf-8 -*-

from urllib.parse import urlparse

import aiohttp

from anquant.config import config
from anquant.utils import logger


class AsyncHttpRequests(object):

    _SESSION = {}

    @classmethod
    def _get_session(cls, url):
        parsed_url = urlparse(url)
        key = parsed_url.netloc or parsed_url.hostname
        if key not in cls._SESSION:
            session = aiohttp.ClientSession()
            cls._SESSION[key] = session
        return cls._SESSION[key]

    @classmethod
    async def fetch(cls, method, url, params=None, body=None,
                    data=None, headers=None, timeout=30, **kwargs):
        session = cls._get_session(url)
        if not kwargs.get("proxy"):
            kwargs["proxy"] = config.proxy
        try:
            if method == "GET":
                response = await session.get(url, params=params, headers=headers,
                                             timeout=timeout, **kwargs)
            elif method == "POST":
                response = await session.post(url, params=params, data=body, json=data,
                                              headers=headers, timeout=timeout, **kwargs)
            elif method == "PUT":
                response = await session.put(url, params=params, data=body, json=data,
                                              headers=headers, timeout=timeout, **kwargs)
            elif method == "DELETE":
                response = await session.delete(url, params=params, data=body, json=data,
                                              headers=headers, timeout=timeout, **kwargs)
            else:
                error = "http method error"
                return None, None, error
        except Exception as e:
            logger.error("method:", method, "url:", url, "params:", params, "body:", body, "data:",
                         data, "Error:", e, caller=cls)
        code = response.status
        if code not in (200, 201, 202, 203, 204, 205, 206):
            text = await response.text()
            logger.error("method:", method, "url:", url, "params:", params, "body:", body, "headers:", headers,
                         "code:", code, "result:", text, caller=cls)
            return code, None, text
        try:
            result = await response.json()
        except:
            logger.warn("response data is not json format!", "method:", method, "url:", url, "params:", params,
                        caller=cls)
            result = await response.text()
        logger.debug("method:", method, "url:", url, "params:", params, "body:", body, "data:", data,
                     "code:", code, "result:", result, caller=cls)
        return code, result, None

    @classmethod
    async def get(cls, url, params=None, body=None, data=None, headers=None, timeout=30, **kwargs):
        result = await cls.fetch("GET", url, params, body, data, headers, timeout, **kwargs)
        return result

    @classmethod
    async def post(cls, url, params=None, body=None, data=None, headers=None, timeout=30, **kwargs):
        result = await cls.fetch("POST", url, params, body, data, headers, timeout, **kwargs)
        return result

    @classmethod
    async def delete(cls, url, params=None, body=None, data=None, headers=None, timeout=30, **kwargs):
        result = await cls.fetch("DELETE", url, params, body, data, headers, timeout, **kwargs)
        return result

    @classmethod
    async def put(cls, url, params=None, body=None, data=None, headers=None, timeout=30, **kwargs):
        result = await cls.fetch("PUT", url, params, body, data, headers, timeout, **kwargs)
        return result
