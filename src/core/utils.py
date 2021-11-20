import os
import random

import aiohttp
import requests

from src.core.settings import TG_TOKEN, ADMINS, proxy_list
from .logger import logger


def check_folders(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def send_message(message: str):
    """
    Веб-сервис, который отправляет сообщения
    от пользователя в телеграм администраторам
    """
    for admin in ADMINS:
        requests.get(
            f'https://api.telegram.org/bot{TG_TOKEN}'
            f'/sendmessage?chat_id={admin}&text={message}'
        )


async def async_request(
        session: aiohttp.ClientSession,
        url: str, *,
        headers=None,
        cookies=None
):
    if headers is None:
        headers = {}
    if cookies is None:
        cookies = {}

    for proxy in random.sample(proxy_list, len(proxy_list)):
        async with session.get(
            url=url, headers=headers, cookies=cookies, proxy=proxy
        ) as res:
            print(res.status)
            if res.status != 200:
                logger.error(f"Status code {res.status} != 200|Proxy: {proxy}")
                continue
            return await res.text()

