import os

import requests

from src.core.settings import TG_TOKEN, ADMINS


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
