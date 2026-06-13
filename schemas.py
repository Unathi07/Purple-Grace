from pydantic import BaseModel, EmailStr

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
    is_active: bool
    model_config={"from_attributes": True}

class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str

