import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# Use a separate test database so tests don't touch your real data
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the test database
Base.metadata.create_all(bind=engine)

# Override the get_db dependency to use the test database instead
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# ---- TESTS ----

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Purple Grace Store!"}

def test_create_product():
    response = client.post("/products", json={
        "name": "Scented Candle",
        "description": "Lavender scented candle",
        "price": 49.99,
        "stock": 20
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Scented Candle"
    assert data["price"] == 49.99
    assert "id" in data  # database assigned an id

def test_get_products():
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_single_product():
    # First create one so we know it exists
    create = client.post("/products", json={
        "name": "Test Product",
        "description": "For testing",
        "price": 10.00,
        "stock": 5
    })
    product_id = create.json()["id"]

    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["id"] == product_id

def test_get_product_not_found():
    response = client.get("/products/99999")
    assert response.status_code == 404

def test_search_products():
    # Create a product to search for
    client.post("/products", json={
        "name": "Purple Soap",
        "description": "Handmade soap",
        "price": 25.00,
        "stock": 15
    })
    response = client.get("/products/search?name=Purple")
    assert response.status_code == 200
    assert any("Purple" in p["name"] for p in response.json())

def test_update_product():
    create = client.post("/products", json={
        "name": "Old Name",
        "price": 10.00,
        "stock": 5
    })
    product_id = create.json()["id"]

    response = client.put(f"/products/{product_id}", json={
        "name": "New Name",
        "price": 15.00,
        "stock": 5
    })
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    assert response.json()["price"] == 15.00

def test_delete_product():
    create = client.post("/products", json={
        "name": "To Be Deleted",
        "price": 5.00,
        "stock": 1
    })
    product_id = create.json()["id"]

    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 200

    # Confirm it's actually gone
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 404

def test_filter_products():
    client.post("/products", json={
        "name": "Lavender Soap",
        "price": 30.00,
        "stock": 10,
        "category": "soap"
    })

    response = client.get("/products/filter?category=soap")
    assert response.status_code == 200
    assert any(p["category"] == "soap" for p in response.json())

    response = client.get("/products/filter?min_price=20&max_price=50")
    assert response.status_code == 200

# Auth Tests

def test_register():
    response = client.post("/register", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data  # password must never be returned

def test_register_duplicate_email():
    # Register once
    client.post("/register", json={
        "email": "duplicate@example.com",
        "password": "password123"
    })
    # Try to register again with same email
    response = client.post("/register", json={
        "email": "duplicate@example.com",
        "password": "password123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login():
    # Register first
    client.post("/register", json={
        "email": "login@example.com",
        "password": "password123"
    })
    # Then login
    response = client.post("/login", data={
        "username": "login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password():
    client.post("/register", json={
        "email": "wrongpass@example.com",
        "password": "correctpassword"
    })
    response = client.post("/login", data={
        "username": "wrongpass@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_login_nonexistent_user():
    response = client.post("/login", data={
        "username": "nobody@example.com",
        "password": "password123"
    })
    assert response.status_code == 401

# Cart Tests

def get_auth_token():
    """Helper function — registers a user and returns their JWT token"""
    client.post("/register", json={
        "email": "cartuser@example.com",
        "password": "password123"
    })
    response = client.post("/login", data={
        "username": "cartuser@example.com",
        "password": "password123"
    })
    return response.json()["access_token"]


def test_add_to_cart():
    token = get_auth_token()

    # Create a product first
    product = client.post("/products", json={
        "name": "Cart Candle",
        "price": 49.99,
        "stock": 10
    }).json()

    response = client.post("/cart", json={
        "product_id": product["id"],
        "quantity": 2
    }, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == product["id"]
    assert data["quantity"] == 2


def test_add_same_product_increases_quantity():
    token = get_auth_token()

    product = client.post("/products", json={
        "name": "Double Candle",
        "price": 49.99,
        "stock": 10
    }).json()

    # Add once
    client.post("/cart", json={
        "product_id": product["id"],
        "quantity": 1
    }, headers={"Authorization": f"Bearer {token}"})

    # Add again
    response = client.post("/cart", json={
        "product_id": product["id"],
        "quantity": 2
    }, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["quantity"] == 3   # 1 + 2


def test_get_cart():
    token = get_auth_token()

    response = client.get("/cart", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_remove_from_cart():
    token = get_auth_token()

    product = client.post("/products", json={
        "name": "Removable Candle",
        "price": 49.99,
        "stock": 10
    }).json()

    # Add to cart
    cart_item = client.post("/cart", json={
        "product_id": product["id"],
        "quantity": 1
    }, headers={"Authorization": f"Bearer {token}"}).json()

    # Remove it
    response = client.delete(
        f"/cart/{cart_item['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_add_to_cart_unauthenticated():
    """Should fail without a token"""
    response = client.post("/cart", json={
        "product_id": 1,
        "quantity": 1
    })
    assert response.status_code == 401


def test_add_nonexistent_product_to_cart():
    token = get_auth_token()

    response = client.post("/cart", json={
        "product_id": 99999,
        "quantity": 1
    }, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404

# ── Order Tests ───────────────────────────────────────────────────────────────

def get_auth_token_orders():
    """Helper — registers a unique user for order tests and returns their token"""
    client.post("/register", json={
        "email": "orderuser@example.com",
        "password": "password123"
    })
    response = client.post("/login", data={
        "username": "orderuser@example.com",
        "password": "password123"
    })
    return response.json()["access_token"]


def test_checkout():
    token = get_auth_token_orders()

    # Create a product
    product = client.post("/products", json={
        "name": "Order Candle",
        "price": 49.99,
        "stock": 10
    }).json()

    # Add it to cart
    client.post("/cart", json={
        "product_id": product["id"],
        "quantity": 2
    }, headers={"Authorization": f"Bearer {token}"})

    # Checkout
    response = client.post("/orders", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2
    assert data["items"][0]["price"] == 49.99


def test_checkout_empty_cart():
    """Checking out with an empty cart should fail"""
    token = get_auth_token_orders()

    response = client.post("/orders", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Your cart is empty"


def test_checkout_clears_cart():
    """After checkout the cart should be empty"""
    token = get_auth_token_orders()

    product = client.post("/products", json={
        "name": "Clearable Candle",
        "price": 25.00,
        "stock": 5
    }).json()

    client.post("/cart", json={
        "product_id": product["id"],
        "quantity": 1
    }, headers={"Authorization": f"Bearer {token}"})

    # Checkout
    client.post("/orders", headers={"Authorization": f"Bearer {token}"})

    # Cart should now be empty
    cart = client.get("/cart", headers={"Authorization": f"Bearer {token}"}).json()
    assert cart == []


def test_get_orders():
    token = get_auth_token_orders()

    response = client.get("/orders", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_order():
    token = get_auth_token_orders()

    product = client.post("/products", json={
        "name": "Single Order Candle",
        "price": 35.00,
        "stock": 5
    }).json()

    client.post("/cart", json={
        "product_id": product["id"],
        "quantity": 1
    }, headers={"Authorization": f"Bearer {token}"})

    order = client.post("/orders", headers={"Authorization": f"Bearer {token}"}).json()

    response = client.get(f"/orders/{order['id']}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == order["id"]


def test_get_order_not_found():
    token = get_auth_token_orders()

    response = client.get("/orders/99999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_orders_unauthenticated():
    """Should fail without a token"""
    response = client.get("/orders")
    assert response.status_code == 401