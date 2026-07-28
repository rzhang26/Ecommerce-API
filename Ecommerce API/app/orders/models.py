from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from enum import StrEnum

class Order(SQLModel, table=True):
    __tablename__ = 'orders'

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key='users.id', nullable=False)
    total_amount_in_cents: int = Field(default=0, nullable=False)
    
    # Use standard string forward-references for the typing declaration
    items: List['OrderItem'] = Relationship(back_populates='order')


class OrderItem(SQLModel, table=True):  
    __tablename__ = 'order_items'

    id: Optional[int] = Field(default=None, primary_key=True)
    
    order_id: int = Field(foreign_key='orders.id', nullable=False)
    product_id: int = Field(foreign_key='products.id', nullable=False)
    
    quantity: int = Field(default=1, nullable=False)
    price_at_purchase_in_cents: int = Field(nullable=False)

    order: Order = Relationship(back_populates='items') #the equivalents of a join in sql

class OrderStatus(StrEnum):
    COMPLETED = 'completed'
    PENDING = 'pending'
    CANCELLED = 'cancelled'

class OrderItemRequest(SQLModel):
    product_id: int
    quantity: int= Field(ge=0, description='Quantity must >= 0.')

class OrderItemResponse(SQLModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: int

class OrderResponse(SQLModel):
    id: Optional[int]  
    user_id: int 
    total_amount_in_cents: int 
    items: List[OrderItemResponse] 
    status: OrderStatus 

class OrderCreate(SQLModel):
    items: List[OrderItemRequest]

Order.model_rebuild()
OrderItem.model_rebuild()