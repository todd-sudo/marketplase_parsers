import time
from typing import Union

import requests

from .exceptions import StatusCodeError


def generate_links_image(product_id: Union[int, str]):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                  "image/avif,image/webp,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) "
                      "Gecko/20100101 Firefox/94.0"
    }
    gen_id = product_id[:4] + "0000"
    urls = list()
    for i in range(20):
        if i == 0:
            continue
        url = f"https://images.wbstatic.net/big" \
              f"/new/{gen_id}/{product_id}-{i}.jpg"
        res = requests.get(url=url, headers=headers)
        if res.status_code == 200:
            urls.append(url)
        else:
            break
        time.sleep(2)

    return urls
