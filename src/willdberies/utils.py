import json
from typing import Union

import aiohttp
from bs4 import BeautifulSoup

from .schemas.sellers_schema import Supplier


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
    async with session.get(url=url, headers=headers, cookies=cookies) as res:
        html = await res.text()
        soup = BeautifulSoup(html, "lxml")
        full_name = soup.find(class_="same-part-kt__header").text.strip()
        composition = soup.find(
            class_="collapsable__content j-consist"
        ).text.strip()
        description = soup.find(class_="j-description")\
            .find(class_="collapsable__text").text.strip()

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
