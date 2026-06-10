from pydantic import BaseModel

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