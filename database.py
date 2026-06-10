from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define where the SQLite database file will live on your machine
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# Create the database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Each time a request comes in, we give it a fresh database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database table models will inherit from this class.
Base = declarative_base()

# Helper function to get a database session and close it automatically when the web request is done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()