import json

import requests

from .schemas import CategoryData
from ..core import check_folders


def get_category():
    """ Получает все категории товаров с ozon
    https://www.ozon.ru/api/composer-api.bx/_action/categoryChildV2?menuId=1&categoryId=15500
    """
    cookies = {
        "__Secure-access-token": "3.0.IFN-UY30QQWgBgWF3yUEoQ.23.l8cMBQAAAABhhltnCQ17rKN3ZWKgAICQoA..20211119172602.AQTAxhK2JkATyEHAfqgJZ3Lt7VOM-H3R4BScUBHTF78",
        "xcid": "afcf5a618ebf6ea8a0263c09919fd8b2",
        "__Secure-refresh-token": "3.0.IFN-UY30QQWgBgWF3yUEoQ.23.l8cMBQAAAABhhltnCQ17rKN3ZWKgAICQoA..20211119172602.7mw6gevFYoQTEfLLg5SC7rhbZ--kNUr-iCu04vLCgA8"
    }
    headers = {
        "User-Agent": "Mozilla/5.0(X11;Ubuntu;Linux x86_64;rv:94.0) Gecko/20100101 Firefox/94.0",
        "x-o3-app-name": "dweb_client",
        "x-o3-app-version": "release_hotfix_9-10'-'2021_91962d2f"
    }

    categories = list()
    url = "https://www.ozon.ru/api/composer-api.bx/_action/" \
          "categoryChildV2?menuId=1&categoryId=15500"
    response = requests.get(url=url, cookies=cookies, headers=headers).json()

    category_data = CategoryData(**response)
    path = "data/ozon/category"
    check_folders(path)

    cd_category = category_data.categories[:-1]
    for cat in cd_category:
        for c in cat.categories:
            categories.append(
                {
                    "id": c.id,
                    "title": c.title,
                    "url": c.url
                }
            )
    with open(f"{path}/category.json", "w") as file:
        json.dump(categories, file, indent=4, ensure_ascii=False)
