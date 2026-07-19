import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.config import get_settings, Settings
from app.database import get_session

# --- CRITICAL FIX: Import all your models here so SQLModel registers them! ---
from app.users.models import User
from app.products.models import Product
from app.orders.models import Order  # Adjust this line to match your filenames


TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

def get_settings_override():
    return Settings(
        DATABASE_URL="sqlite:///:memory:",
        JWT_SECRET_KEY="STATIC_TEST_SECRET_KEY_FOR_JWT_SIGNING_BOUNDARIES",
        ACCESS_TOKEN_EXPIRE_MIN=30
    )

def get_session_override():
    with Session(test_engine) as session:
        yield session

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    # Now that models are imported, this will successfully build all tables
    SQLModel.metadata.create_all(test_engine)
    
    app.dependency_overrides[get_settings] = get_settings_override
    app.dependency_overrides[get_session] = get_session_override
    
    yield
    
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture(scope="function")
def client():
    with TestClient(app) as test_client:
        yield test_client