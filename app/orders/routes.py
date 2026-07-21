from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.database import get_session
from app.orders.models import Order, OrderResponse, OrderCreate, OrderItem, OrderItemRequest, OrderItemResponse, OrderStatus
from app.products.models import Product
from app.users.dependencies import get_current_user
from app.users.models import User


router = APIRouter(prefix='/orders', tags=['Order & Checkout'])


@router.post('/', response_model = OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout_shopping_cart(order_in: OrderCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if not order_in.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Cannot process an empty order canvas.'
        )
    
    master_order = Order(
        user_id=current_user.id,
        status=OrderStatus.COMPLETED,
        total_amount_in_cents=0
    )
    session.add(master_order)
    session.flush()

    calculated_total_accumulation = 0

    for item in order_in.items:
        product = session.get(Product, item.product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item referencing inventory product ID {item.product_id} no longer exists."
            )
        if product.inventory_count < item.quantity:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Inadequate inventory stock options for {product.name}.'
            )
    
        product.inventory_count -= item.quantity
        session.add(product)

        line_item_total = product.price_in_cents * item.quantity
        calculated_total_accumulation += line_item_total

        db_order_item = OrderItem(
            order_id=master_order.id,
            product_id=product.id,
            quantity=item.quantity,
            price_at_purchase_in_cents=product.price_in_cents
        )
        session.add(db_order_item)
    
    master_order.total_amount_in_cents = calculated_total_accumulation
    session.add(master_order)
    
    session.commit()
    session.refresh(master_order)

    return master_order

@router.get('/my-history', response_model=List[OrderResponse])
def get_user_order_history(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    statement = select(Order).where(Order.user_id == current_user.id).order_by(Order.created_at.desc())
    orders = session.exec(statement).all()
    if not orders:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"This user has no order history."
            )

    return orders