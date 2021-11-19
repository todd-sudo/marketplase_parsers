import json
import os

import requests


def parse_category():
    """ Парсит категории 
    https://www.wildberries.ru/gettopmenuinner?lang=ru
    """
    url = "https://www.wildberries.ru/gettopmenuinner?lang=ru"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3"
    }
    response = requests.get(url=url, headers=headers)
    urls = list()
    result = response.json()
    categories = result.get("value").get("menu")
    for category in categories:
        try:
            name = category.get("name")
            base_url = category.get("pageUrl")
            childs = category.get("childs")
            
            for child in childs:
                ch_url = child.get("pageUrl")
                ch_childs = child.get("childs")
                print(type(ch_childs))
                for ch_child in ch_childs:
                    c_url = ch_child.get("pageUrl")

                    obj = {
                        "category_name": name,
                        "url": f"{base_url}/{ch_url}/{c_url}"
                    }
                    urls.append(obj)

            print(name)
        except Exception as e:
            print(e)
            continue

    path = "data"
    if not os.path.exists(path):
        os.mkdir(path)

    with open(f"{path}/category.json", "w") as file:
        json.dump(urls, file, indent=4, ensure_ascii=False)


def main():
    parse_category()


if __name__ == "__main__":
    main()
