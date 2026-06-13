# Standard library
from typing import List

# Third-party
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Local
import auth
import models
import schemas
from database import engine, get_db

# Creates the database file and all tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Purple Grace Store")

# Tells FastAPI where the login endpoint is so it can handle token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = auth.decode_access_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Home

@app.get("/")
def home():
    return {"message": "Welcome to Purple Grace Store!"}

# Get product by searching the name
@app.get("/products/search", response_model=List[schemas.ProductResponse])
def search_products(name: str, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(
        models.Product.name.ilike(f"%{name}%")
    ).all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found")

    return products

# Filter by category and/or price
@app.get("/products/filter", response_model=List[schemas.ProductResponse])
def filter_products(
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Product)

    if category:
        query = query.filter(models.Product.category.ilike(f"%{category}%"))

    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)

    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)

    products = query.all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found")

    return products


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
@app.get("/products/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

# Update existing products
@app.put("/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, updated: schemas.ProductCreate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in updated.model_dump().items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product

# Remove products
@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": f"Product {product_id} deleted successfully"}

# Authentication
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        email=user.email,
        hashed_password=auth.hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

# Cart

# Add item to cart
@app.post("/cart", response_model=schemas.CartItemResponse)
def add_to_cart(
    item: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # ← must be logged in
):
    # Check the product actually exists
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if this product is already in the user's cart
    existing = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id,
        models.CartItem.product_id == item.product_id
    ).first()

    if existing:
        # Just increase the quantity instead of adding a duplicate
        existing.quantity += item.quantity
        db.commit()
        db.refresh(existing)
        return existing

    # Create a new cart item
    cart_item = models.CartItem(
        user_id=current_user.id,
        product_id=item.product_id,
        quantity=item.quantity
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item


# View cart
@app.get("/cart", response_model=List[schemas.CartItemResponse])
def get_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # ← must be logged in
):
    items = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id
    ).all()
    return items


# Remove item from cart
@app.delete("/cart/{item_id}")
def remove_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # ← must be logged in
):
    item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id,
        models.CartItem.user_id == current_user.id  # can only delete your own items
    ).first()

    if item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(item)
    db.commit()
    return {"message": "Item removed from cart"}

# Orders 

# Checkout — converts cart into an order
@app.post("/orders", response_model=schemas.OrderResponse)
def checkout(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Get the user's cart
    cart_items = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id
    ).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Your cart is empty")

    # Create the order
    from datetime import datetime, timezone
    order = models.Order(
        user_id=current_user.id,
        status="pending",
        created_at=datetime.now(timezone.utc).isoformat()
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Convert each cart item into an order item
    order_items = []
    for cart_item in cart_items:
        product = db.query(models.Product).filter(
            models.Product.id == cart_item.product_id
        ).first()

        order_item = models.OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=product.price   # snapshot the price at checkout
        )
        db.add(order_item)
        order_items.append(order_item)

    # Clear the cart
    for cart_item in cart_items:
        db.delete(cart_item)

    db.commit()

    # Attach items to the order for the response
    order.items = order_items
    return order


# View order history
@app.get("/orders", response_model=List[schemas.OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    orders = db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    ).all()

    # Attach items to each order
    for order in orders:
        order.items = db.query(models.OrderItem).filter(
            models.OrderItem.order_id == order.id
        ).all()

    return orders


# Get a single order
@app.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id  # can only see your own orders
    ).first()

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    order.items = db.query(models.OrderItem).filter(
        models.OrderItem.order_id == order.id
    ).all()

    return order