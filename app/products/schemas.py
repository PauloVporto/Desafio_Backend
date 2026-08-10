from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str = Field(default="", max_length=1000)
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    status: str = Field(default="Ativo")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("Nome não pode ser vazio.")
        return value

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str):
        return value.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str):
        value = value.strip()
        if value not in {"Ativo", "Inativo"}:
            raise ValueError("Status deve ser Ativo ou Inativo.")
        return value


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
