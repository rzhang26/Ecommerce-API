from typing import Optional
from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

class ProductBase(SQLModel):
    model_config = ConfigDict(from_attributes = True)

    name: str = Field(index=True, unique=True, nullable=False)
    description: Optional[str] = Field(default=None)
    price_in_cents: int = Field(default=0)
    inventory_count: int = Field(default=0)

class Product(ProductBase, table=True):
    __tablename__ = 'products'
    id: Optional[int] = Field(default=None, primary_key=True)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    pass
