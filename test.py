import asyncio
import json
import os.path
import random
import time
from typing import Union

import aiohttp
import requests


from src.willdberies import exceptions
from src.willdberies.schemas.product_schema import Object
from src.willdberies.schemas.list_product_schema import Data, CategoryData
from src.willdberies.utils import (
    get_pagination
)
# from ..core.settings import proxies, proxy
from src.core.utils import check_folders, send_message
from src.core.logger import logger





async def get_products_id():

    ids = list()
    path_id = "data/wildberries/ids"
    path_category = "data/wildberries/category"
    check_folders(path_id)
    check_folders(path_category)

    page = get_pagination()

    print(f"Pages - {page}")
    for p in range(page):
        list_category = list()
        if p == 0:
            continue
        print(f"Page - {p}")
        url = f"https://www.wildberries.ru/catalogdata/zhenshchinam/" \
              f"odezhda/bryuki-i-shorty/?page={p}?sort=popular"

        async with aiohttp.ClientSession() as session:
            response = await session.get(url=url)
            res_text = await response.text()
            res = json.loads(res_text)

            if response.status != 200:
                logger.error(f"Status code {response.status} != 200")
                # send_message(
                #     f"Status code {res.status} != 200\nВозможно получен бан!")
                raise exceptions.StatusCodeError(
                    f"Status code {response.status} != 200"
                )

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

        for pr_id in result.value.data.model.products:
            ids.append(str(pr_id.product_id))
        await asyncio.sleep(1)

    with open(f"{path_id}/id.json", "w") as file:
        json.dump(ids, file, indent=4, ensure_ascii=False)

    return len(ids)


def run_parser_wb():
    start_time = time.monotonic()
    asyncio.run(get_products_id())
    print(f"Потрачено времени: {(time.monotonic() - start_time) / 60} минут")


def main():
    run_parser_wb()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
