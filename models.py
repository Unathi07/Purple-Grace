from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class Product(Base):
    __tablename__ = "Products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    category = Column(String, nullable=True)

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

class CartItem(Base):
    __tablename__ = "CartItems"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)      
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)