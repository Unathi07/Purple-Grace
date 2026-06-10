from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    description: str | None=None
    price: float| int
    stock: int

class ProductResponse(ProductCreate):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}