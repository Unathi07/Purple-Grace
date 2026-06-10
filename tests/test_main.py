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