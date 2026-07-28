from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import Optional, List
from sqlmodel import Session, select

from app.orders.models import Order, OrderCreate, OrderItem, OrderItemRequest, OrderItemResponse, OrderResponse, OrderStatus
from app.users.models import User
from app.products.models import Product
from app.users.dependencies import get_current_user
from app.database import get_session, SessionDep

router = APIRouter(prefix='/orders', tags=['Order & OrderItems'])

@router.post('/', response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout_shopping_cart(order_in: OrderCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if not order_in.items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Cannot process an empty order.'
        )

    master_order = Order(
        user_id=current_user.id,
        status=OrderStatus.COMPLETED,
        total_amount_in_cents=0
    )
    session.add(master_order) #not needed but idempotent so good
    session.flush()

    accumulated_total = 0
    for item in order_in.items:
        product = session.get(Product, item.product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Item referencing inventory product ID {item.product_id} cannot be found or no longer exists.'
            )
        if product.inventory_count < item.quantity:
            session.rollback() #similar to a 'continue' equivalent for session open/closings
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Inqdequate stock for {product.name} in the inventory.'
            )

        product.inventory_count -= item.quantity
        session.add(product)

        accumulated_total += item.quantity * product.price_in_cents

        db_order_item = OrderItem(
            order_id=master_order.id,
            product_id=product.id,
            quantity=item.quantity,
            price_at_purchase_in_cents=product.price_in_cents
        )
        session.add(db_order_item)

    master_order.total_amount_in_cents = accumulated_total
    session.add(master_order)

    session.commit()
    session.refresh(master_order)

    return master_order

@router.get('/my-history', response_model=OrderResponse)
def get_user_order_history(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    statement = select(Order).where(Order.user_id == current_user.id).order_by(Order.user_id.desc())
    orders = session.exec(statement).all()
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No orders can be retrieved for user {current_user.id}.'
        )

    return orders