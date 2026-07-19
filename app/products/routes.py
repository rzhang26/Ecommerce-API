from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.products.models import Product, ProductBase, ProductCreate, ProductResponse, ProductUpdate
from app.users.dependencies import get_current_user
from app.users.models import User

router = APIRouter(
    prefix='/products',
    tags=['Catalog & Products']
)

@router.get('/', response_model=List[ProductResponse])
def list_catalog_products(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    statement = select(Product).offset(skip).limit(limit)
    products = session.exec(statement).all()

    return products

@router.get('/{product_id}', response_model=ProductResponse)
def get_product_details(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} does not exist."
        )
    
    return product

@router.post('/',response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_new_product(product_in: ProductCreate, session: Session = Depends(get_session)):
    new_product = Product.model_validate(product_in) #???
    session.add(new_product)
    session.commit()
    session.refresh(new_product)

    return new_product

@router.put('/{product_id}', response_model=ProductResponse)
def update_product_inventory(product_id: int, product_in: ProductUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Taget catalog product not found.'
        )
    
    payload = product_in.model_dump(exclude_unset=True)
    for key, val in payload.items():
        setattr(db_product, key, val)

    session.add(db_product)
    session.commit()
    session.refresh(db_product)

    return db_product

@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Taget catalog product not found.'
        )
    
    session.delete(product)
    session.commit()
    return None