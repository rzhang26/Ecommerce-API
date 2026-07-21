from sqlmodel import SQLModel, Field, Relationship
from enum import StrEnum
from typing import List, Optional
from zoneinfo import ZoneInfo

EASTERN_TZ = ZoneInfo('America/New_York')

class OrderStatus(StrEnum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class OrderItemRequest(SQLModel):
    product_id: int
    quantity: int = Field(gt=0, description='Quantity must be >= 0.')

class OrderCreate(SQLModel):
    items: List[OrderItemRequest]

class OrderItemResponse(SQLModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase_in_cents: int 

class OrderResponse(SQLModel):
    id: int
    user_id: int
    total_amount_in_cents: int
    status: OrderStatus
    items: List[OrderItemResponse]


# class OrderItem(SQLModel, tabke=True):
#     __tablename__ = 'order_items'

#     id: Optional[int] = Field(default=None, primary_key=True)
#     order_id: Optional[int] = Field(default=None, foreign_key='order.id', nullable=False)
#     product_id: int = Field(default=None, foreign_key='product.id', nullable=False)
#     quantity: int = Field(nullable=False)
#     price_at_purchase: int = Field(nullable=False, description='Preserves unit pricing historical context')

#     order: 'Order' = Relationship(back_populates='items')

# class Order(SQLModel, table=True):
#     __tablename__ = 'orders'

#     id: Optional[int] = Field(default=None, primary_key=True)
#     user_id: Optional[int] = Field(foreign_key='users.id', nullable=False)
#     total_amount_in_cents: int = Field(default=0, nullable=False)
#     status: OrderStatus = Field(default=OrderStatus.PENDING, nullable=False)
#     created_at: datetime = Field(default_factory=lambda: datetime.now(EASTERN_TZ), nullable=False)

#     items: List[OrderItem] = Relationship(back_populates='order')

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


#Forces Pydantic & SQLModel to compile type resolution mappings immediately
Order.model_rebuild()
OrderItem.model_rebuild()