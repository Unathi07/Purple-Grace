# Purple Grace Store 🛍️

A fully functional e-commerce REST API built with Python and FastAPI, developed as both a portfolio project and a real-world store for a small business.

## Features

- 🛒 Product management with search and filter by category and price
- 👤 User registration and login with secure password hashing (bcrypt)
- 🔐 JWT token authentication and protected routes
- 🛍️ Shopping cart with quantity management
- 📦 Order system with checkout and order history
- ✅ Full test suite with 27 passing tests

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.14 | Programming language |
| FastAPI | Web framework |
| SQLAlchemy | Database ORM |
| SQLite | Database |
| bcrypt | Password hashing |
| python-jose | JWT tokens |
| pytest | Testing |

## Project Structure

```
Purple-Grace/
├── routers/
│   ├── __init__.py
│   ├── products.py       # product endpoints
│   ├── auth.py           # register + login
│   ├── cart.py           # cart endpoints
│   └── orders.py         # order endpoints
├── tests/
│   ├── conftest.py       # shared test setup
│   ├── test_products.py
│   ├── test_auth.py
│   ├── test_cart.py
│   └── test_orders.py
├── main.py               # app entry point
├── models.py             # database models
├── schemas.py            # pydantic schemas
├── auth.py               # JWT logic
├── dependencies.py       # shared dependencies
├── database.py           # database connection
└── requirements.txt
```

## Getting Started

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/Purple-Grace.git
cd Purple-Grace
```

**2. Create and activate a virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the server**
```bash
uvicorn main:app --reload
```

**5. Open the interactive API docs**
```
http://127.0.0.1:8000/docs
```

## Running Tests

```bash
pytest tests/ -v
```

## API Endpoints

### Products
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/products` | Get all products | No |
| GET | `/products/{id}` | Get single product | No |
| GET | `/products/search?name=` | Search by name | No |
| GET | `/products/filter` | Filter by category/price | No |
| POST | `/products` | Create a product | No |
| PUT | `/products/{id}` | Update a product | No |
| DELETE | `/products/{id}` | Delete a product | No |

### Auth
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/register` | Create an account | No |
| POST | `/login` | Login and receive JWT token | No |

### Cart
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/cart` | View your cart | ✅ |
| POST | `/cart` | Add item to cart | ✅ |
| DELETE | `/cart/{id}` | Remove item from cart | ✅ |

### Orders
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/orders` | View order history | ✅ |
| GET | `/orders/{id}` | View single order | ✅ |
| POST | `/orders` | Checkout | ✅ |

## How Authentication Works

1. Register at `POST /register` with your email and password
2. Login at `POST /login` to receive a JWT token
3. Include the token in the `Authorization` header for protected routes:
```
Authorization: Bearer <your_token>
```

## Author

**Unathi Makhubela**  
Third year Computer Science student at the University of the Western Cape  
[GitHub](https://github.com/yourusername)
