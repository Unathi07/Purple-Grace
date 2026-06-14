# Standard library
import os
import hashlib
from urllib.parse import urlencode

# Third-party
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Local
from database import get_db
from dependencies import get_current_user
import models

load_dotenv()

MERCHANT_ID = os.getenv("PAYFAST_MERCHANT_ID")
MERCHANT_KEY = os.getenv("PAYFAST_MERCHANT_KEY")
PASSPHRASE = os.getenv("PAYFAST_PASSPHRASE")

# For testing
PAYFAST_URL = "https://sandbox.payfast.co.za/eng/process"

# Public URL
BASE_URL = "http://127.0.0.1:8000"

router = APIRouter(prefix="/payments", tags=["Payments"])


def generate_signature(data: dict, passphrase: str = None) -> str:
    """Generate PayFast MD5 signature from payment data"""
    # Sort the data alphabetically
    sorted_data = {k: v for k, v in sorted(data.items())}
    # Build the query string
    query_string = urlencode(sorted_data)
    # Add passphrase if provided
    if passphrase:
        query_string += f"&passphrase={passphrase}"
    # Return MD5 hash
    return hashlib.md5(query_string.encode()).hexdigest()


@router.post("/pay/{order_id}")
def initiate_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a PayFast payment for an order and redirect to payment page"""

    # Get the order
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status == "paid":
        raise HTTPException(status_code=400, detail="Order already paid")

    # Get order items and calculate total
    items = db.query(models.OrderItem).filter(
        models.OrderItem.order_id == order.id
    ).all()

    total = sum(item.price * item.quantity for item in items)

    # Build PayFast payment data
    payment_data = {
        "merchant_id": MERCHANT_ID,
        "merchant_key": MERCHANT_KEY,
        "return_url": f"{BASE_URL}/static/payment-success.html",
        "cancel_url": f"{BASE_URL}/static/orders.html",
        "notify_url": f"{BASE_URL}/payments/notify",
        "name_first": current_user.email.split("@")[0],
        "email_address": current_user.email,
        "m_payment_id": str(order.id),
        "amount": f"{total:.2f}",
        "item_name": f"Purple Grace Store Order #{order.id}",
    }

    # Generate signature
    payment_data["signature"] = generate_signature(payment_data, PASSPHRASE)

    # Redirect to PayFast
    query_string = urlencode(payment_data)
    return RedirectResponse(url=f"{PAYFAST_URL}?{query_string}")


@router.post("/notify")
async def payment_notify(request: dict, db: Session = Depends(get_db)):
    """
    PayFast calls this endpoint after a successful payment.
    Updates the order status to 'paid'.
    """
    order_id = request.get("m_payment_id")
    payment_status = request.get("payment_status")

    if payment_status == "COMPLETE":
        order = db.query(models.Order).filter(
            models.Order.id == int(order_id)
        ).first()
        if order:
            order.status = "paid"
            db.commit()

    return {"status": "ok"}