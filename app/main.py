from fastapi import FastAPI
from app.users.routes import router as users_router
from app.products.routes import router as products_router
from app.orders.routes import router as orders_router

from app.users.models import User
from app.products.models import Product
from app.orders.models import Order, OrderItem


app = FastAPI(title='E-commerce API')
app.include_router(users_router)
app.include_router(products_router)
app.include_router(orders_router)


@app.get('/')
def root():
    return {'message': 'hello world, welcome to my ready e-commerce API'}