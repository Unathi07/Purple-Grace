# Standard library
import os

# Third-party
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Local
from database import get_db
import models
import schemas

load_dotenv()

# Admin password loaded from .env — never hardcoded
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

router = APIRouter(prefix="/admin", tags=["Admin"])


def verify_admin(password: str):
    """Check if the provided password matches the admin password"""
    if password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin password"
        )


# Admin Auth

@router.post("/login")
def admin_login(password: str):
    """Verify admin password — returns success if correct"""
    verify_admin(password)
    return {"admin": True}


# Admin Product Management 

@router.get("/products")
def admin_get_products(
    password: str,
    db: Session = Depends(get_db)
):
    """Get all products including inactive ones — admin only"""
    verify_admin(password)
    return db.query(models.Product).all()


@router.delete("/products/{product_id}")
def admin_delete_product(
    product_id: int,
    password: str,
    db: Session = Depends(get_db)
):
    """Permanently delete a product — admin only"""
    verify_admin(password)
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}


@router.put("/products/{product_id}", response_model=schemas.ProductResponse)
def admin_update_product(
    product_id: int,
    password: str,
    updated: schemas.ProductCreate,
    db: Session = Depends(get_db)
):
    """Update an existing product — admin only"""
    verify_admin(password)
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in updated.model_dump().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product