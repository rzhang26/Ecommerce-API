import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

# Importing them registers them with SQLModel.metadata
from app.main import app
from app.users.models import User, UserBase, UserCreate, UserResponse
from app.database import get_session, engine as main_engine
from app.products.models import Product, ProductBase, ProductCreate, ProductUpdate, ProductResponse
from app.orders.models import Order, OrderItem, OrderCreate, OrderItemRequest, OrderItemResponse, OrderResponse, OrderStatus

TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

@pytest.fixture(name="session", autouse=True)
def session_fixture():
    # Build tables on the test engine
    SQLModel.metadata.create_all(test_engine)
    
    with Session(test_engine) as session:
        yield session
        
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    # Override get_session to return the active test session
    def get_session_override():
        yield session
        
    app.dependency_overrides[get_session] = get_session_override
    
    with TestClient(app) as client:
        yield client
        
    app.dependency_overrides.clear()