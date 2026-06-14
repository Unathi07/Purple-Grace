# Standard library
from typing import List

# Third-party
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Local
from database import engine
import models
from routers import products, auth, cart, orders

# Creates all database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Purple Grace Store")

# Serve static files from the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(cart.router)
app.include_router(orders.router)

@app.get("/")
def home():
    return FileResponse("static/index.html")