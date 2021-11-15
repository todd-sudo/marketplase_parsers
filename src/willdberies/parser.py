import json
import time
from typing import Union

import requests

from .schemas import Object
from .utils import generate_links_image


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
    url = f"https://wbxcatalog-ru.wildberries.ru/nm-2-card/catalog?spp=3&lang=ru&curr=rub&offlineBonus=0&onlineBonus=0&emp=0&locale=ru&nm=11708541"
    res = requests.get(url=url, headers=headers)
    time.sleep(2)
    images = generate_links_image("11708541")

    data = Object(**res.json())
    objects = list()
    colors = list()
    sizes = list()
    stocks = list()

    for product in data.data.products:
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
        promo_sale = product.extended.promo_sale
        # promo_price = int(product.extended.promo_price) / 100 or None
        for color in product.colors:
            color_name = color.name
            color_id = color.color_id
            colors.append({"name": color_name, "color_id": color_id})

        for size in product.sizes:
            for stock in size.stocks:
                warehouse = stock.warehouse
                qty = stock.qty
                stocks.append({"warehouse": warehouse, "qty": qty})

            sizes.append({
                "size_name": size.name,
                "orig_name": size.orig_name,
                "stocks": stocks
            })

        obj = {
            "url": f"https://www.wildberries.ru/catalog/{id_product}/detail.aspx",
            "id_product": id_product,
            "name": name,
            "brand": brand,
            "brand_id": brand_id,
            "price_u": price_u or None,
            "sale": sale or None,
            "sale_price": sale_price or None,
            "rating": rating,
            "feedbacks": feedbacks or None,
            "basic_sale": basic_sale or None,
            "basic_price_u": basic_price_u or None,
            "promo_sale": promo_sale or None,
            # "promo_price": promo_price or "",
            "colors": colors or None,
            "sizes": sizes or None,
            "images": images
        }

        objects.append(obj)

        print(objects)

    with open("main.json", "w") as file:
        json.dump(objects, file, indent=4, ensure_ascii=False)
