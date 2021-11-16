from typing import List, Union

from pydantic import BaseModel, Field


class BModel(BaseModel):
    class Config:
        @classmethod
        def alias_generator(cls, string: str) -> str:
            # this is the same as `alias_generator = to_camel`
            # sample_field => sampleField
            first, *l = string.split("_")
            s = [first] + [word.capitalize() for word in l]
            return "".join(s)


class Extended(BModel):
    basic_sale: int = 0
    basic_price_u: int = 0
    # client_sale: Union[int, float, None] = Field(alias="clientSale")
    # client_price: Union[int, float, None] = Field(alias="clientPriceU")
    promo_sale: int = 0
    promo_price: int = 0


class Color(BaseModel):
    name: Union[str]
    color_id: int = Field(alias="id")


class Stock(BaseModel):
    warehouse: Union[int, None] = Field(alias="wh")
    qty: Union[int, None]


class Size(BaseModel):
    name: str = None
    orig_name: str = Field(alias="origName")
    stocks: Union[List[Stock]]


class Product(BaseModel):
    product_id: int = Field(alias="id")
    name: str = None
    brand: str = None
    brand_id: int = Field(alias="brandId")
    price_u: Union[int, float] = Field(alias="priceU")
    sale: Union[int, float] = None
    sale_price: Union[int, float] = Field(alias="salePriceU", default=None)
    extended: Extended = None
    rating: Union[int, None]
    feedbacks: Union[int, None]
    colors: List[Color]
    sizes: List[Size]


# class BaseProduct(BaseModel):
#     first: int = Field(alias="0")


class Image(BaseModel):
    url: str


class Data(BaseModel):
    products: List[Product]


class Object(BaseModel):
    data: Data
    # url: str
    # images: List[Image]
