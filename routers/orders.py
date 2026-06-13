from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from dependencies import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("", response_model=schemas.OrderResponse)
def checkout(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    cart_items = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id
    ).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Your cart is empty")
    order = models.Order(
        user_id=current_user.id,
        status="pending",
        created_at=datetime.now(timezone.utc).isoformat()
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    order_items = []
    for cart_item in cart_items:
        product = db.query(models.Product).filter(
            models.Product.id == cart_item.product_id
        ).first()
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=product.price
        )
        db.add(order_item)
        order_items.append(order_item)
    for cart_item in cart_items:
        db.delete(cart_item)
    db.commit()
    order.items = order_items
    return order

@router.get("", response_model=List[schemas.OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    orders = db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    ).all()
    for order in orders:
        order.items = db.query(models.OrderItem).filter(
            models.OrderItem.order_id == order.id
        ).all()
    return orders

@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order.items = db.query(models.OrderItem).filter(
        models.OrderItem.order_id == order.id
    ).all()
    return order