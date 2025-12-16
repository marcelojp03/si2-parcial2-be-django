# E-Commerce Backend

[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.1-red.svg)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-blue.svg)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/AWS-S3%20%7C%20RDS%20%7C%20App%20Runner-orange.svg)](https://aws.amazon.com/)

REST API backend for e-commerce platform with multi-warehouse inventory, product variants, shopping cart, payment gateway integration (VPAY, QR), and AI-powered analytics reports using OpenAI GPT-4o-mini.

---

## Features

- **JWT Authentication** with token blacklist
- **Product catalog** with variants and dynamic attributes (EAV model)
- **Multi-warehouse inventory** with stock reservation system
- **Shopping cart** with persistent storage
- **Checkout flow** with multiple payment providers (VPAY, QR, MOCK)
- **Order management** with status tracking
- **AI-powered reports** using OpenAI GPT-4o-mini
- **S3 image storage** with presigned URLs
- **Role-based access control** (RBAC)
- **Analytics module** with data warehouse (sale facts)

---

## Prerequisites

- Python >= 3.11
- PostgreSQL 14+
- AWS Account (S3, RDS, App Runner)
- OpenAI API Key (optional, for AI reports)
- npm or yarn (for frontend)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/marcelojp03/si2-parcial2-be-django.git
cd ecommerce-django-be
```

### 2. Create virtual environment

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory:

```env
# Django
SECRET_KEY="your-secret-key-here"
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_USER=postgres
DB_PASS=your-password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce
DB_SCHEMA=si2-ecommerce

# AWS
AWS_REGION=us-east-1
AWS_PROFILE=default  # For local development

# JWT
JWT_SECRET_KEY=your-jwt-secret

# OpenAI (optional)
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
LLM_MODEL=gpt-4o-mini
```

### 5. Setup database

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Populate sample data (optional)

```bash
python scripts/populate_db.py
```

---

## Running the Application

### Development mode

```bash
python manage.py runserver
```

### Production mode (Gunicorn)

```bash
gunicorn ecommerce.wsgi:application --bind 0.0.0.0:1112 --workers 2 --threads 4
```

### Deploy to AWS App Runner

```bash
# Build and push Docker image to ECR
docker build -f Dockerfile.prod -t eshop-be .
docker tag eshop-be:latest 851725478821.dkr.ecr.us-east-1.amazonaws.com/eshop-be:latest
docker push 851725478821.dkr.ecr.us-east-1.amazonaws.com/eshop-be:latest
```

Server runs on `http://localhost:8000/api`

**Production:** `https://ggppjnr4rk.us-east-1.awsapprunner.com`

---

## API Modules

| Module | Endpoints | Description |
|--------|-----------|-------------|
| **Auth** | `/api/auth/login`, `/api/auth/register`, `/api/auth/refresh` | JWT authentication |
| **Catalog** | `/api/catalog/products`, `/api/catalog/categories` | Product management |
| **Inventory** | `/api/inventory/warehouses`, `/api/inventory/inventory` | Stock management |
| **Cart** | `/api/sales/carts`, `/api/sales/cart-items` | Shopping cart |
| **Orders** | `/api/sales/orders`, `/api/sales/checkout` | Order processing |
| **Payments** | `/api/sales/payments` | Payment handling (VPAY, QR, MOCK) |
| **Analytics** | `/api/analytics/reports` | AI-powered reports |
| **Customers** | `/api/customers/` | Customer profiles |

---

## Project Structure

```
ecommerce-django-be/
├── apps/
│   ├── administration/     # Users, roles, RBAC
│   ├── catalog/            # Products, categories, variants
│   ├── inventory/          # Warehouses, stock
│   ├── sales/              # Orders, cart, payments
│   ├── customers/          # Customer profiles
│   ├── analytics/          # Reports, forecasting
│   └── core/               # Shared utilities
├── docs/                   # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── API_QUICK_REFERENCE.md
│   ├── DATABASE_STRUCTURE.md
│   ├── DEPLOYMENT.md
│   └── postman_collection.json
├── scripts/                # Utility scripts
│   └── populate_db.py
├── ecommerce/              # Django settings
├── Dockerfile.prod         # Production Docker image
├── entrypoint.py           # Startup script
├── requirements.txt
└── manage.py
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) | Complete API reference with examples |
| [docs/API_QUICK_REFERENCE.md](docs/API_QUICK_REFERENCE.md) | Quick endpoint reference |
| [docs/DATABASE_STRUCTURE.md](docs/DATABASE_STRUCTURE.md) | Complete database schema (35 tables) |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | AWS deployment guide (ECR + App Runner) |
| [docs/postman_collection.json](docs/postman_collection.json) | Postman collection for testing |

---

## Tech Stack

- **Framework:** Django 5.2.7
- **API:** Django REST Framework 3.16.1
- **Database:** PostgreSQL (AWS RDS)
- **Storage:** AWS S3 (product images)
- **Authentication:** JWT with SimpleJWT
- **Payment:** VPAY, QR Code
- **AI:** OpenAI GPT-4o-mini (reports)
- **Deployment:** AWS App Runner + ECR
- **Language:** Python 3.11

---

## License

MIT
