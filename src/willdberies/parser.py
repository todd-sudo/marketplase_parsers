import asyncio
import json
import time
from typing import Union

import aiohttp
import requests

from . import exceptions
from .schemas.product_schema import Object
from .schemas.list_product_schema import Data, CategoryData
from .utils import (
    generate_links_image,
    get_sellers,
    get_detail_info_for_product,
    get_name_warehouse,
    save_data_json,
    get_pagination
)
from ..core.utils import check_folders
from ..core.logger import logger


headers = {
    "Host": "wbxcatalog-ru.wildberries.ru",
    "Connection": "keep-alive",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-A205FN) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "SamsungBrowser/15.0 "
                  "Chrome/90.0.4430.210 Mobile Safari/537.36",
    "Origin": "https://www.wildberries.ru",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}


async def parse_object(
        product_id: str, place_on_page: Union[int, str], category_info
) -> dict:
    """ Парсит продукт по product_id и возвращает список продуктов
    """

    url = f"https://wbxcatalog-ru.wildberries.ru/nm-2-card/catalog?" \
          f"spp=3&lang=ru&curr=rub&offlineBonus=0&onlineBonus=" \
          f"0&emp=0&locale=ru&nm={product_id}"

    async with aiohttp.ClientSession() as session:
        res = await session.get(url=url, headers=headers)
        if res.status != 200:
            logger.error(f"Status code {res.status} != 200")
            raise exceptions.StatusCodeError(
                f"Status code {res.status} != 200"
            )
        images = await generate_links_image(product_id, session)
        sellers = await get_sellers(product_id, session)
        details = await get_detail_info_for_product(product_id, session)

        response = await res.text()
        response_json = json.loads(response)
        data = Object(**response_json)

        product = data.data.products[0]
        id_product = product.product_id or None
        category_name = product.name or None
        brand = product.brand or None
        brand_id = product.brand_id or None
        price_u = product.price_u / 100 or None
        sale = product.sale or 0
        sale_price = product.sale_price / 100 or 0
        rating = product.rating or None
        count_feedbacks = product.feedbacks or None

        try:
            basic_sale = product.extended.basic_sale
        except AttributeError:
            basic_sale = 0
        try:
            basic_price_u = product.extended.basic_price_u / 100
        except AttributeError:
            basic_price_u = 0
        try:
            promo_sale = product.extended.promo_sale
        except AttributeError:
            promo_sale = 0
        try:
            promo_price = product.extended.promo_price / 100
        except AttributeError:
            promo_price = 0
        colors = list()

        for color in product.colors:
            color_name = color.name or None
            color_id = color.color_id or None
            colors.append({"name": color_name, "color_id": color_id})
        sizes = list()

        for size in product.sizes:
            stocks = list()
            for stock in size.stocks:
                warehouse = stock.warehouse or None
                wh_name = get_name_warehouse(warehouse) or ""
                qty = stock.qty or 0
                stocks.append({
                    "warehouse": warehouse,
                    "qty": qty,
                    "warehouse_name": wh_name
                })

            sizes.append({
                "size_name": size.name or None,
                "orig_name": size.orig_name or None,
                "stocks": stocks,
            })

    obj = {
        "category_info": category_info,
        f"{id_product}": {
            "url": f"https://www.wildberries.ru/catalog/{id_product}/detail.aspx",
            "id_product": id_product,
            "place_on_page": place_on_page,
            "category_name": category_name,
            "brand": brand,
            "brand_id": brand_id,
            "details": details,
            "рейтинг": rating,
            "цена": price_u,
            "общая_скидка": sale,
            "цена_продажи": sale_price,
            "скидка": basic_sale,
            "цена_со_скидкой": basic_price_u,
            "промокод": promo_sale,
            "цена_с_промокодом": promo_price,
            "количество_отзывов": count_feedbacks or None,
            "colors": colors or None,
            "sizes": sizes or None,
            "sellers": sellers,
            "images": images
        }
    }

    return obj


def get_products_id(page: int):
    """ Получает id продукта и запускает таску на его парсинг

        https://www.wildberries.ru/catalogdata/zhenshchinam/odezhda/bryuki-i-shorty/?page=1
1699
    """

    url = f"https://www.wildberries.ru/catalogdata/zhenshchinam/" \
          f"odezhda/bryuki-i-shorty/?page={page}?sort=popular"
    res = requests.get(url=url)
    if res.status_code != 200:
        logger.error(f"Status code {res.status_code} != 200")
        raise exceptions.StatusCodeError(
            f"Status code {res.status_code} != 200"
        )

    result = Data(**res.json())

    list_category = list()
    categories = result.value.data.model.category_info
    for c in categories:
        json_data = json.loads(c.info)
        category_data = CategoryData(**json_data)
        list_category.append({
            "position": category_data.position,
            "subject_id": category_data.subject_id
        })

    ids = list()
    for pr_id in result.value.data.model.products[:6]:
        ids.append(str(pr_id.product_id))
        time.sleep(2)

    return ids, list_category


@logger.catch
async def gather_data():
    """Запускает сбор данных"""
    products = list()
    page = get_pagination()
    ids, list_categories = get_products_id(page=1)
    place_on_page = 1
    # for pr_id in ids:
    product = await parse_object("33844157", place_on_page, list_categories)
    products.append(product)
    await asyncio.sleep(1)

    path = "data/wildberries"
    check_folders(path)
    save_data_json(
        products=products,
        path=path,
        filename="wb"
    )
