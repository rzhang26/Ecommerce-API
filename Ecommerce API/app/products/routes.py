from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import Optional, List
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.products.models import Product, ProductBase, ProductCreate, ProductUpdate, ProductResponse
from app.users.models import User
from app.users.dependencies import get_current_user
from app.database import get_session, SessionDep

router = APIRouter(prefix='/products', tags=['Catalogue & Products'])

@router.get('/', response_model=List[ProductResponse])
def list_catalogue_products(session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=0)):
    statement = select(Product).offset(offset).limit(limit)
    products = session.exec(statement).all()
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Catalogue of products cannot be found.'
        )

    return products

@router.get('/{product_id}', response_model=ProductResponse)
def get_product_details(product_id: int, session: Session = Depends(get_session)):
    product_info = session.get(Product, product_id)
    if not product_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'No product of product id #{product_id} can be found.'
        )

    return product_info

@router.post('/', response_model=ProductResponse)
def create_new_product(product_in: ProductCreate, session: Session = Depends(get_session)):
    new_product = Product.model_validate(product_in)

    try:
        session.add(new_product) #unique=True for name so is ok 
        session.commit()
    except IntegrityError: 
        session.rollback() # Clean up the failed transaction
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'A product of the name {product_in.name} already exists.'
        )

    session.refresh(new_product)

    return new_product

@router.put('/{product_id}', response_model=Product)
def update_product(product_id: int, product_in: ProductUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)): 
    Product.model_validate(product_in)
    
    new_product = session.get(Product, product_id).first()
    if not new_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Target catalog product not found.'
        )

    payload = product_in.model_dump(exclude_unset=True)
    for key, val in payload.items():
        setattr(new_product, key, val)

    session.add(new_product)
    session.commit()
    session.refresh(new_product)

    return new_product

@router.delete('/{product_id}')
def delete_product(product_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No product of product id #{product_id} can be found.'
        )
    
    session.delete(product)
    session.commit()
    
    return None