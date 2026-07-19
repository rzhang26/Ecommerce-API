from sqlmodel import select
from app.users.models import User  # Adjust import path to your User model
import pytest
from fastapi import status
from sqlmodel import Session
from tests.conftest import test_engine  # <-- FORCE IT TO USE THE TEST ENGINE

def test_complete_ecommerce_checkout_lifecycle(client):
    user_payload = {
        "email": "test_insufficient@example.com",
        "username": "test_insufficient",  # If your Pydantic model requires 'username'
        "password": "password123"
    }
    
    register_resp = client.post("/users/", json=user_payload)
    
    # If this still asserts 422, print the exact validation error to your terminal:
    assert register_resp.status_code == 201, f"Registration failed schema validation: {register_resp.json()}"

    # --- DIAGNOSTIC BLOCK ---
    # We inspect the database directly through the test client's app state or engine
    from app.database import engine  # Adjust import to your test/app engine
    with Session(test_engine) as session:
        users = session.exec(select(User)).all()
        print(f"\n--- DEBUG DB USERS (Count: {len(users)}) ---")
        for u in users:
            print(f"ID: {u.id} | Email: {u.email} | Username: {getattr(u, 'username', 'N/A')} | Hash: {u.hashed_password[:15]}...")
    # ------------------------

    login_response = client.post(
        "/users/login", 
        data={"username": "test@example.com", "password": "password123"}
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    
    token_data = login_response.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # --- PHASE 3: Seed Catalog Product (Requires Authentication) ---
    product_payload = {
        "name": "Mechanical Keyboard",
        "description": "Tactile clicky switches",
        "price_in_cents": 9900,  # $99.00
        "inventory_count": 5
    }
    prod_response = client.post("/products/", json=product_payload, headers=headers)
    assert prod_response.status_code == status.HTTP_201_CREATED
    product_id = prod_response.json()["id"]

    # --- PHASE 4: Atomic Checkout Processing (Protected) ---
    checkout_payload = {
        "items": [
            {"product_id": product_id, "quantity": 2}
        ]
    }
    order_response = client.post("/orders/", json=checkout_payload, headers=headers)
    
    assert order_response.status_code == status.HTTP_201_CREATED
    order_data = order_response.json()
    assert order_data["total_amount_in_cents"] == 19800  # 9900 * 2
    assert order_data["status"] == "completed"
    assert len(order_data["items"]) == 1
    assert order_data["items"][0]["quantity"] == 2

    # --- PHASE 5: Verify Inventory Deduction ---
    catalog_check = client.get(f"/products/{product_id}")
    assert catalog_check.status_code == status.HTTP_200_OK
    assert catalog_check.json()["inventory_count"] == 3


def test_checkout_fails_if_insufficient_stock(client):
    """Ensures that the database rolls back and fails if stock limits are breached."""
    # 1. Register and login with clean payload checking
    user_payload = {
        "email": "buyer@example.com",
        "username": "buyer@example.com",
        "password": "password123"
    }
    register_resp = client.post("/users/", json=user_payload)
    assert register_resp.status_code in [200, 201], f"Registration failed: {register_resp.text}"

    login_response = client.post(
        "/users/login", 
        data={"username": "buyer@example.com", "password": "password123"}
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Add product with 1 item remaining (and include description)
    product_payload = {
        "name": "Last Mug", 
        "description": "Limited stock item",
        "price_in_cents": 1500, 
        "inventory_count": 1
    }
    prod_resp = client.post("/products/", json=product_payload, headers=headers)
    assert prod_resp.status_code == status.HTTP_201_CREATED
    product_id = prod_resp.json()["id"]

    # 3. Attempt to buy 2 items (violates inventory)
    failed_order = client.post("/orders/", json={
        "items": [{"product_id": product_id, "quantity": 2}]
    }, headers=headers)

    assert failed_order.status_code == status.HTTP_400_BAD_REQUEST
    
    # Check for keywords like "stock" or "inventory" to avoid rigid phrasing brittle assertions
    error_detail = failed_order.json()["detail"]
    assert any(word in error_detail.lower() for word in ["stock", "inventory", "inadequate", "insufficient"])