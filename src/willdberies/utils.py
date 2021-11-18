import json
from datetime import datetime
from typing import Union

import aiohttp
import requests
from bs4 import BeautifulSoup

from . import exceptions
from .schemas.list_product_schema import Data
from .schemas.sellers_schema import Supplier
from ..core import logger
from ..core.settings import proxies, proxy

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) "
                  "Gecko/20100101 Firefox/94.0"
}


async def generate_links_image(
        product_id: Union[int, str], session: aiohttp.ClientSession
):
    """Генерирует ссылку на изображение продукта"""
    gen_id = product_id[:4] + "0000"
    urls = list()
    for i in range(20):
        if i == 0:
            continue
        url = f"https://images.wbstatic.net/big" \
              f"/new/{gen_id}/{product_id}-{i}.jpg"
        async with session.get(url=url, headers=headers) as response:
            if response.status == 200:
                urls.append(url)
            else:
                break
            # time.sleep(2)
    return urls


async def get_sellers(
        product_id: Union[str, int], session: aiohttp.ClientSession
):
    """Получает поставщика"""
    objects = list()
    url = f"https://wbx-content-v2.wbstatic.net/sellers/" \
          f"{product_id}.json?locale=ru"
    async with session.get(url=url, headers=headers) as response:
        res = await response.text()
        r = json.loads(res)
        data = Supplier(**r)
        objects.append({
            "supplier_id": data.supplier_id or None,
            "supplier_name": data.supplier_name or None,
            "inn": data.inn or None,
            "ogrn": data.ogrn or None,
            "address": data.address or None
        })
    return objects


async def get_detail_info_for_product(
        product_id: Union[str, int], session: aiohttp.ClientSession
):
    """ Получает детальную информацию от продукте, путем парсинга HTML
    """
    cookies = {
        "_wbauid": "320633131636902673",
        "BasketUID": "538c7d14-121b-4b0c-9a70-bf14810a00e2"
    }
    url = f"https://www.wildberries.ru/catalog/{product_id}/detail.aspx"
    async with session.get(url=url, headers=headers, cookies=cookies, proxy=proxy) as res:
        html = await res.text()
        soup = BeautifulSoup(html, "lxml")
        try:
            full_name = soup.find(class_="same-part-kt__header").text.strip()
        except Exception as e:
            full_name = ""
        composition = soup.find(
            class_="collapsable__content j-consist"
        ).text.strip()
        try:
            description = soup.find(class_="j-description")\
                .find(class_="collapsable__text").text.strip()
        except Exception as e:
            description = ""

        # specifications
        table = soup.find(class_="product-params__table")
        trs = table.find_all(class_="product-params__row")
        specifications = list()
        for tr in trs:
            key = tr.find("th").text.strip()
            value = tr.find("td").text.strip()
            specifications.append({key: value})

    detail = {
        "full_name": full_name,
        "composition": composition,
        "description": description,
        "specifications": specifications
    }
    return detail


def get_name_warehouse(wh_id: int):
    """ Возвращает имя склада по его id
    """
    wh_name = ""
    if wh_id == 117501:
        wh_name = "Коледино"
    elif wh_id == 507:
        wh_name = "Подольск"
    elif wh_id in [121709, 120769, 120762]:
        wh_name = "Электросталь"
    elif wh_id == 2737:
        wh_name = "Санкт-Петербург"
    elif wh_id in [130744, 1699]:
        wh_name = "Краснодар"
    elif wh_id == 117986:
        wh_name = "Казань"
    elif wh_id == 1733:
        wh_name = "Екатеринбург"
    elif wh_id == 686:
        wh_name = "Новосибирск"
    elif wh_id == 1193:
        wh_name = "Хабаровск"
    return wh_name


def get_pagination() -> int:
    """Возвращает число стариниц"""
    url = f"https://www.wildberries.ru/" \
          f"catalogdata/zhenshchinam/odezhda/bryuki-i-shorty/?page=1"
    res = requests.get(url=url, proxies=proxies)
    if res.status_code != 200:
        logger.error(f"Status code {res.status_code} != 200")
        raise exceptions.StatusCodeError(
            f"Status code {res.status_code} != 200"
        )
    result = Data(**res.json())
    return result.value.data.model.pager_model.paging_info.total_pages


def save_data_json(products: list, path: str, filename: str, flag: str):
    current_datetime = datetime.now().strftime("%d.%m.%Y__%H:%M:%S")
    with open(f"{path}/{filename}_{current_datetime}.json", f"{flag}") as file:
        json.dump(products, file, indent=4, ensure_ascii=False)
