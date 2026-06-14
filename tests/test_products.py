from tests.conftest import client

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "Purple Grace" in response.text

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
    assert "id" in data

def test_get_products():
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_single_product(sample_product):
    response = client.get(f"/products/{sample_product['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == sample_product["id"]

def test_get_product_not_found():
    response = client.get("/products/99999")
    assert response.status_code == 404

def test_search_products():
    client.post("/products", json={
        "name": "Purple Soap",
        "price": 25.00,
        "stock": 15
    })
    response = client.get("/products/search?name=Purple")
    assert response.status_code == 200
    assert any("Purple" in p["name"] for p in response.json())

def test_update_product(sample_product):
    response = client.put(f"/products/{sample_product['id']}", json={
        "name": "Updated Candle",
        "price": 59.99,
        "stock": 5
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Candle"

def test_delete_product(sample_product):
    response = client.delete(f"/products/{sample_product['id']}")
    assert response.status_code == 200
    response = client.get(f"/products/{sample_product['id']}")
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