import json
from typing import Union

import requests

from .schemas import Object


headers = {
    "Host": "wbxcatalog-ru.wildberries.ru",
    "Connection": "keep-alive",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-A205FN) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/15.0 Chrome/90.0.4430.210 Mobile Safari/537.36",
    "Origin": "https://www.wildberries.ru",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.wildberries.ru/catalog/13396406/detail.aspx?targetUrl=GP",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}

# category = "zhenshchinam/odezhda/bluzki-i-rubashki"
# url = f"https://www.wildberries.ru/catalogdata/{category}/?desktop=2&sort=popular&page=2"


def parse_object():
    url = "https://wbxcatalog-ru.wildberries.ru/nm-2-card/catalog?" \
          "spp=3&lang=ru&curr=rub&offlineBonus=0&" \
          "onlineBonus=0&emp=0&locale=ru&nm=11708541"
    res = requests.get(url=url, headers=headers)
    print(res.status_code)

    data = Object(**res.json())

    print(data)
