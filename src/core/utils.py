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
        headers: dict = None,
        cookies: dict = None
):
    for proxy in random.sample(proxy_list, len(proxy_list)):
        res = await session.get(
            url=url, headers=headers, cookies=cookies, proxy=proxy
        )
        if res.status != 200:
            logger.error(f"Status code {res.status} != 200|Proxy: {proxy}")
            # send_message(
            #     f"Status code {res.status} != 200\n"
            #     f"Возможно получен бан!\nProxy: {proxy}\nДелаю замену..."
            # )
            continue
        return res

