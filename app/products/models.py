from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel, ConfigDict

class ProductBase(SQLModel):
    model_config = ConfigDict(from_attributes=True) 

    name: str = Field(index=True, nullable=False)
    description: Optional[str] = Field(default=None)
    price_in_cents: int = Field(default=0, description='Price stored as an int (eg. $10.50 is 1050)', nullable=False)
    inventory_count: int = Field(default=0, description='Availible stock count')

class ProductCreate(ProductBase):
    #Schema applied to enforce input validation upon creation
    pass
    
class ProductUpdate(BaseModel): #sqlmodel or pydantic BaseModel also works since for post request input validations
    name: Optional[str] = None
    description: Optional[str] = None
    price_in_cents: Optional[int] = None
    inventory_count: Optional[int] = None

class ProductResponse(ProductBase):
    id: int


class Product(ProductBase, table=True):
    __tablename__ = 'products'
    id: Optional[int] = Field(default=None, primary_key=True)

# class Product(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str = Field(unique=True, index=True, nullable=False)
#     description: Optional[str] = Field(default=None)

#     price_in_cents: int = Field(nullable=False)
#     price_in_dollars: int = Field(default=0, nullable=False)

#     order_items: List['OrderItem'] = Relationship(back_populates='product')

