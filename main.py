from fastapi import FastAPI, Depends
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