import asyncio
import json
import os.path
import random
from typing import Union

import aiohttp

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

from ..core.utils import check_folders, send_message, async_request
from ..core.logger import logger


headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-A205FN) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "SamsungBrowser/15.0 "
                  "Chrome/90.0.4430.210 Mobile Safari/537.36",
}


async def parse_object(
        product_id: str,
        place_on_page: Union[int, str],
        category_info,
        session: aiohttp.ClientSession
):
    """ Парсит продукт по product_id и возвращает список продуктов
    """

    url = f"https://wbxcatalog-ru.wildberries.ru/nm-2-card/catalog?" \
          f"spp=3&lang=ru&curr=rub&offlineBonus=0&onlineBonus=" \
          f"0&emp=0&locale=ru&nm={product_id}"

    response = await async_request(session=session, url=url, headers=headers)
    images = await generate_links_image(product_id, session)
    # sellers = await get_sellers(product_id, session)
    # details = await get_detail_info_for_product(product_id, session)

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
            # "details": details,
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
            # "sellers": sellers,
            "images": images
        }
    }

    return obj


async def get_products_id(session: aiohttp.ClientSession):

    ids = list()
    path_id = "data/wildberries/ids"
    path_category = "data/wildberries/category"
    check_folders(path_id)
    check_folders(path_category)

    page = await get_pagination(session=session)

    print(f"Pages - {page}")
    for p in range(page):
        list_category = list()
        if p == 0:
            continue
        print(f"Page - {p}")
        url = f"https://www.wildberries.ru/catalogdata/zhenshchinam/" \
              f"odezhda/bryuki-i-shorty/?page={p}?sort=popular"

        response = await async_request(session=session, url=url)
        res = json.loads(response)
        result = Data(**res)

        if p == 1:
            categories = result.value.data.model.category_info or None
            if categories is not None:
                for c in categories:
                    json_data = json.loads(c.info)
                    category_data = CategoryData(**json_data)
                    list_category.append({
                        "position": category_data.position or None,
                        "subject_id": category_data.subject_id or None
                    })
            with open(f"{path_category}/category.json", "w") as file:
                json.dump(list_category, file, indent=4, ensure_ascii=False)

        for pr_id in result.value.data.model.products[:3]:
            ids.append(str(pr_id.product_id))
        await asyncio.sleep(1)

    with open(f"{path_id}/id.json", "w") as file:
        json.dump(ids, file, indent=4, ensure_ascii=False)

    return len(ids)


@logger.catch
async def gather_data(start: int, finish: int):
    """Запускает сбор данных"""
    path_id = "data/wildberries/ids"
    path_category = "data/wildberries/category"
    path = "data/wildberries"
    temp_path = f"{path}/temp"
    check_folders(path)
    check_folders(temp_path)
    products = list()

    try:
        async with aiohttp.ClientSession() as session:
            len_ids = []
            if not os.path.exists(f"{path_id}/id.json"):
                len_ids = await get_products_id(session=session)

            print(f"Len IDS - {len_ids}")

            with open(f"{path_id}/id.json", "r") as file:
                ids = json.load(file)
            with open(f"{path_category}/category.json", "r") as file:
                list_categories = json.load(file)

            place_on_page = 1
            index = 1
            for pr_id in ids[start:finish]:
                print(f"Parse {pr_id}| {index}/{len(ids)}")
                product = await parse_object(
                    pr_id, place_on_page, list_categories, session
                )
                products.append(product)
                place_on_page += 1
                if len(products) % 100 == 0:
                    await save_data_json(
                        products=products,
                        path=temp_path,
                        filename="temp",
                        flag="a"
                    )
                print(f"Good {pr_id}")
                await asyncio.sleep(random.randint(2, 5))
                index += 1

            await save_data_json(
                products=products,
                path=path,
                filename="wb",
                flag="w"
            )
    except Exception as e:
        logger.error(e)
        send_message(f"{e}\nУпал по неизвестной ошибке! Убиваемся")

    else:
        print("save data")
        send_message("ВСЕ ЗАЕБИСЬ")
