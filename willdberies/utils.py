from typing import Union


def generate_link_image(product_id: Union[int, str], number: Union[int, str]):
    gen_id = product_id[:4] + "0000"
    url = f"https://images.wbstatic.net/c516x688" \
          f"/new/{gen_id}/{product_id}-{number}.jpg"
    return url
