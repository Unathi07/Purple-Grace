from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import engine, get_db
from typing import List
import schemas


# Creates the database file and all tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Purple Grace Store")

@app.get("/")
def home():
    return {"message": "Database and server are successfully linked!"}

# Read all products
@app.get("/products", response_model=List[schemas.ProductResponse])
def get_products(db:Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products

# Create a product
@app.post("/products", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    new_product = models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# Get a single product
@app.get("/producrs/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

# Get product by searching the name
@app.get("products/search", response_model=List[schemas.ProductResponse])
def search_products(name: str, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(
        models.Product.name.ilike(f"%{name}%")
    ).all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found")

    return products

