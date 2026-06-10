from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class Product(Base):
    __tablename__ = "products"  # This sets the actual table name in SQL

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)  # Useful if you want to hide an item temporarily