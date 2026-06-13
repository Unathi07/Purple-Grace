from tests.conftest import client

def test_register():
    response = client.post("/register", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data

def test_register_duplicate_email():
    client.post("/register", json={
        "email": "duplicate@example.com",
        "password": "password123"
    })
    response = client.post("/register", json={
        "email": "duplicate@example.com",
        "password": "password123"
    })
    assert response.status_code == 400

def test_login():
    client.post("/register", json={
        "email": "login@example.com",
        "password": "password123"
    })
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