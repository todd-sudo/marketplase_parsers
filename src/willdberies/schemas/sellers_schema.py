from typing import Union

from pydantic import BaseModel, Field


class Supplier(BaseModel):
    supplier_id: Union[int, str, None] = Field(alias="supplierId")
    supplier_name: Union[str, None] = Field(alias="supplierName")
    inn: Union[str, int, None] = Field(alias="inn")
    ogrn: Union[str, int, None] = Field(alias="ogrn")
    address: Union[str, None] = Field(alias="legalAddress")
