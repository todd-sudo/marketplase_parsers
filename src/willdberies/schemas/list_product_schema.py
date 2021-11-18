from typing import List, Union, Optional

from pydantic import BaseModel, Field


class PagingInfo(BaseModel):
    current_page: Optional[int] = Field(alias="currentPage")
    current_page_size: Optional[int] = Field(alias="currentPageSize")
    total_items: Optional[int] = Field(alias="totalItems")
    total_pages: Optional[int] = Field(alias="totalPages")


class PagerModel(BaseModel):
    paging_info: PagingInfo = Field(alias="pagingInfo")


class IDProduct(BaseModel):
    product_id: Optional[int] = Field(alias="nmId")


class CategoryInfo(BaseModel):
    info: Optional[str] = Field(alias="statisticFieldsJson")


class Model(BaseModel):
    category_info: List[CategoryInfo] = Field(alias="advGoods", default="")
    pager_model: PagerModel = Field(alias="pagerModel")
    products: List[IDProduct]


class MainData(BaseModel):
    model: Model


class Value(BaseModel):
    data: MainData


class Data(BaseModel):
    value: Value


class CategoryData(BaseModel):
    position: Union[int, str, None]
    subject_id: Union[int, str, None] = Field(alias="subjectId")
