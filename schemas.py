from pydantic import BaseModel, EmailStr
from typing import List

# Products
class ProductCreate(BaseModel):
    name: str
    description: str | None=None
    price: float
    stock: int
    category: str | None=None

class ProductResponse(ProductCreate):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}

# Users
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int=1

class CartItemResponse(BaseModel):
    user_id: int
    id: int
    product_id: int
    quantity: int
    model_config = {"from_attributes": True}

class OrderItemResponse(BaseModel):
    """Shape of a single item inside an order"""
    id: int
    product_id: int
    quantity: int
    price: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    """Shape of a full order"""
    id: int
    user_id: int
    status: str
    created_at: str
    items: List[OrderItemResponse] = []

    model_config = {"from_attributes": True}




