from typing import List

from pydantic import BaseModel


class SubCategory(BaseModel):
    id: int = None
    title: str = None
    url: str = None


class Category(BaseModel):
    categories: List[SubCategory] = None


class CategoryData(BaseModel):
    categories: List[Category] = None
