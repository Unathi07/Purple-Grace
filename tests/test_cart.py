from tests.conftest import client

def test_add_to_cart(auth_token, sample_product):
    response = client.post("/cart", json={
        "product_id": sample_product["id"],
        "quantity": 2
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert response.json()["quantity"] == 2

def test_add_same_product_increases_quantity(auth_token, sample_product):
    client.post("/cart", json={
        "product_id": sample_product["id"],
        "quantity": 1
    }, headers={"Authorization": f"Bearer {auth_token}"})
    response = client.post("/cart", json={
        "product_id": sample_product["id"],
        "quantity": 2
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.json()["quantity"] == 3

def test_get_cart(auth_token):
    response = client.get("/cart", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_remove_from_cart(auth_token, sample_product):
    cart_item = client.post("/cart", json={
        "product_id": sample_product["id"],
        "quantity": 1
    }, headers={"Authorization": f"Bearer {auth_token}"}).json()
    response = client.delete(
        f"/cart/{cart_item['id']}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200

def test_add_to_cart_unauthenticated(sample_product):
    response = client.post("/cart", json={
        "product_id": sample_product["id"],
        "quantity": 1
    })
    assert response.status_code == 401

def test_add_nonexistent_product_to_cart(auth_token):
    response = client.post("/cart", json={
        "product_id": 99999,
        "quantity": 1
    }, headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 404