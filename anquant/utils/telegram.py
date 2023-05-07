# -*- coding:utf-8 -*-
from anquant.utils import logger
from anquant.utils.async_http import AsyncHttpRequests


class TelegramBot:
    BASE_URL = "https://api.telegram.org"

    @classmethod
    async def send_text_msg(cls, token, chat_id, content, proxy=None):
        url = "{base_url}/bot{token}/sendMessage?chat_id={chat_id}&text={content}".format(
            base_url=cls.BASE_URL,
            token=token,
            chat_id=chat_id,
            content=content
        )
        result = await AsyncHttpRequests.get(url, proxy=proxy)
        logger.info("url:", url, "result:", result, caller=cls)
