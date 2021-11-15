import asyncio
import json

import aiohttp

from . import exceptions
from .schemas.product_schema import Object
from .schemas.list_product_schema import Data
from .utils import (
    generate_links_image,
    get_sellers,
    get_detail_info_for_product
)


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


async def parse_object(product_id: str) -> dict:
    """ Парсит продукт по product_id и возвращает список продуктов
    """
    url = f"https://wbxcatalog-ru.wildberries.ru/nm-2-card/" \
          f"catalog?spp=3&lang=ru&curr=rub&offlineBonus=0&" \
          f"onlineBonus=0&emp=0&locale=ru&nm={product_id}"

    async with aiohttp.ClientSession() as session:
        res = await session.get(url=url, headers=headers)

        images = await generate_links_image(product_id, session)
        sellers = await get_sellers(product_id, session)
        details = await get_detail_info_for_product(product_id, session)

        response = await res.text()
        response_json = json.loads(response)
        data = Object(**response_json)

        colors = list()
        sizes = list()
        stocks = list()

        product = data.data.products[0]
        # for product in data.data.products:
        id_product = product.product_id
        name = product.name
        brand = product.brand
        brand_id = product.brand_id
        price_u = int(product.price_u) / 100
        sale = product.sale
        sale_price = int(product.sale_price) / 100
        rating = product.rating
        feedbacks = product.feedbacks

        basic_sale = product.extended.basic_sale
        basic_price_u = int(product.extended.basic_price_u) / 100
        promo_sale = product.extended.promo_sale or None
        promo_price = int(product.extended.promo_price) / 100 or None
        for color in product.colors:
            color_name = color.name
            color_id = color.color_id
            colors.append({"name": color_name, "color_id": color_id})

        for size in product.sizes:
            for stock in size.stocks:
                warehouse = stock.warehouse
                qty = stock.qty
                stocks.append({"warehouse": warehouse, "qty": qty})
                break

            sizes.append({
                "size_name": size.name,
                "orig_name": size.orig_name,
            })

        obj = {
            "url": f"https://www.wildberries.ru/catalog/{id_product}/detail.aspx",
            "id_product": id_product,
            "name": name,
            "brand": brand,
            "brand_id": brand_id,
            "details": details,
            "price_u": price_u or None,
            "sale": sale or None,
            "sale_price": sale_price or None,
            "rating": rating,
            "feedbacks": feedbacks or None,
            "basic_sale": basic_sale or None,
            "basic_price_u": basic_price_u or None,
            "promo_sale": promo_sale,
            "promo_price": promo_price,
            "colors": colors or None,
            "sizes": sizes or None,
            "stocks": stocks,
            "sellers": sellers,
            "images": images
        }

    return obj
    # with open("main.json", "w") as file:
    #     json.dump(obj, file, indent=4, ensure_ascii=False)


async def get_products_id():
    """ Получает id продукта и запускает таску на его парсинг

    https://www.wildberries.ru/catalogdata/zhenshchinam/odezhda/bryuki-i-shorty/?&page=1
    """
    url = "https://www.wildberries.ru/catalogdata/zhenshchinam/odezhda/bryuki-i-shorty/?&page=1"
    async with aiohttp.ClientSession(headers=headers) as session:
        res = await session.get(url=url, headers=headers, max_redirects=30)
        if res.status != 200:
            raise exceptions.StatusCodeError(f"Status code {res.status} != 200")
        data = await res.text()
        print(data)
        result_json = json.loads(data)
        result = Data(**result_json)

        products = list()

        product_count = result.value.model.pager_model.paging_info.current_page_size

        for pr_id in result.value.model.products:
            obj = await parse_object(str(pr_id))
            products.append(obj)
            print(f"{pr_id} - {len(products)}/{product_count}")
            await asyncio.sleep(2)

    return products
