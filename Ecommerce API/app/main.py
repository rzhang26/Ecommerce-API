from fastapi import FastAPI
from sqlmodel import SQLModel, Session, select
from contextlib import asynccontextmanager

from app.products.models import Product
from app.users.routes import router as user_router
from app.orders.routes import router as order_router
from app.products.routes import router as product_router
from app.database import engine


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        first_data = session.exec(select(Product)).first()
        if not first_data: 
            session.add_all([
                Product(name='garlic fish soup', description='yum yum', price_in_cents=1984, inventory_count=20),
                Product(name='garlic naan bread', description='yum yum yum', price_in_cents=1984, inventory_count=30)
            ])
            session.commit()
        yield


app = FastAPI(title='Ecommerce API', lifespan=lifespan)

app.include_router(user_router)
app.include_router(order_router)
app.include_router(product_router)

@app.get('/')
async def homepage():
    return {'Homepage': 'Hello World'}