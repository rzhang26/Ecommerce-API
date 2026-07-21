import pytest
from fastapi import status
from app.users.models import User
from app.users.security import hash_password

def test_create_user_successful(client, session):
    """Happy Path: Ensure a user can register with valid data."""
    payload = {"email": "newuser@example.com", "password": "securepassword123"}
    
    response = client.post("/users/", json=payload)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data  # Ensure plain text password isn't leaked

def test_create_user_duplicate_email_fails(client, session):
    """Edge Case: Registering an email that already exists should fail or be handled securely."""
    # Arrange: Pre-seed a user into the isolated test database
    existing_user = User(email="duplicate@example.com", hashed_password=hash_password("password"))
    session.add(existing_user)
    session.commit()
    
    payload = {"email": "duplicate@example.com", "password": "anotherpassword"}
    
    # Act
    response = client.post("/users/", json=payload)
    
    # Assert
    # Note: Depending on your global exception handlers for IntegrityError (Unique Constraint),
    # this will return a 400 or 409 if handled, or a 500 if unhandled. 
    # You should catch SQLAlchemy's IntegrityError in your route to return a clean 400.
    assert response.status_code == status.HTTP_400_BAD_REQUEST or response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.parametrize("invalid_payload", [
    {"email": "not-an-email", "password": "validpassword"},  # Invalid email format
    {"email": "test@example.com"},                          # Missing password field
    {"password": "justapassword"},                          # Missing email field
])
def test_create_user_invalid_data_fails(client, invalid_payload):
    """Edge Case: Input structure variations must be caught by Pydantic validation rules."""
    response = client.post("/users/", json=invalid_payload)
    
    # assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_successful(client, session):
    """Happy Path: Standard OAuth2 login returns a valid token structure."""
    # Arrange: Seed a valid user
    raw_password = "mypassword"
    user = User(email="login_test@example.com", hashed_password=hash_password(raw_password))
    session.add(user)
    session.commit()
    
    # Act: OAuth2 Password Form transmits data as form-urlencoded, not JSON
    form_data = {"username": "login_test@example.com", "password": raw_password}
    response = client.post("/users/login", data=form_data)
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_incorrect_password_fails(client, session):
    """Edge Case: Valid email but incorrect password yields a 401 Unauthorized."""
    user = User(email="login_test@example.com", hashed_password=hash_password("correct_password"))
    session.add(user)
    session.commit()
    
    form_data = {"username": "login_test@example.com", "password": "wrong_password"}
    response = client.post("/users/login", data=form_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password."


def test_read_profile_unauthenticated_fails(client):
    """Edge Case: Accessing protected '/me' route without headers yields a 401."""
    response = client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED