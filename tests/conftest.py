import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    """Wipe all tables before each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture
def auth_token():
    """Register a user and return their token"""
    client.post("/register", json={
        "email": "testuser@example.com",
        "password": "password123"
    })
    response = client.post("/login", data={
        "username": "testuser@example.com",
        "password": "password123"
    })
    return response.json()["access_token"]

@pytest.fixture
def sample_product():
    """Create and return a sample product"""
    response = client.post("/products", json={
        "name": "Test Candle",
        "price": 49.99,
        "stock": 10,
        "category": "candles"
    })
    return response.json()