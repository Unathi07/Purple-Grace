from tests.conftest import client

def test_checkout(auth_token, sample_product):
    client.post("/cart", json={
        "product_id": sample_product["id"],
        "quantity": 2
    }, headers={"Authorization": f"Bearer {auth_token}"})
    response = client.post("/orders", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert len(data["items"]) == 1

def test_checkout_empty_cart(auth_token):
    response = client.post("/orders", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 400

def test_checkout_clears_cart(auth_token, sample_product):
    client.post("/cart", json={
        "product_id": sample_product["id"],
        "quantity": 1
    }, headers={"Authorization": f"Bearer {auth_token}"})
    client.post("/orders", headers={"Authorization": f"Bearer {auth_token}"})
    cart = client.get("/cart", headers={"Authorization": f"Bearer {auth_token}"}).json()
    assert cart == []

def test_get_orders(auth_token):
    response = client.get("/orders", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_single_order(auth_token, sample_product):
    client.post("/cart", json={
        "product_id": sample_product["id"],
        "quantity": 1
    }, headers={"Authorization": f"Bearer {auth_token}"})
    order = client.post("/orders", headers={"Authorization": f"Bearer {auth_token}"}).json()
    response = client.get(f"/orders/{order['id']}", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert response.json()["id"] == order["id"]

def test_get_order_not_found(auth_token):
    response = client.get("/orders/99999", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 404

def test_orders_unauthenticated():
    response = client.get("/orders")
    assert response.status_code == 401