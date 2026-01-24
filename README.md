# Autoship Hub Backend

This repository contains the backend service for Autoship Hub, a platform designed to streamline shipping and trade documentation processes. It is built using Python and FastAPI, providing a robust RESTful API for managing users, proforma invoices, and letters of credit (LCs).

The system features OCR capabilities to extract data from uploaded Letter of Credit PDF documents and can generate proforma invoices in PDF format.

## Key Features

-   **RESTful API:** A modern, asynchronous API built with FastAPI.
-   **User Management:** User registration and JWT-based authentication.
-   **Role-Based Access Control:** Differentiated access permissions for users (e.g., `admin`).
-   **Proforma Invoice Management:** Create, approve, reject, and retrieve proforma invoices.
-   **PDF Generation:** Dynamically generate PDF documents for proforma invoices using WeasyPrint.
-   **Letter of Credit (LC) Processing:** Extract data from LC documents in PDF format using an external OCR model.
-   **Database Integration:** Uses SQLAlchemy ORM for interacting with a PostgreSQL database.
-   **Containerized Environment:** Fully dockerized for easy setup and deployment.

## Technology Stack

-   **Backend:** Python 3.11, FastAPI
-   **Database:** PostgreSQL, SQLAlchemy
-   **Authentication:** JWT, Passlib, Python-JOSE
-   **Containerization:** Docker, Docker Compose
-   **PDF/OCR:** WeasyPrint (PDF Generation), `pdf2image`, and an external OCR service (e.g., Ollama) for data extraction.
-   **Dependency Management:** Pip

## Project Structure

The project follows a standard structure for FastAPI applications:

```
├── app/
│   ├── api/              # API endpoints, routers, and dependencies
│   ├── core/             # Configuration and security modules
│   ├── db/               # Database session and base models
│   ├── models/           # SQLAlchemy ORM models
│   ├── repositories/     # Data access layer (Repository Pattern)
│   ├── schemas/          # Pydantic schemas for data validation
│   ├── services/         # Business logic layer
│   ├── templates/        # Jinja2 templates for PDF generation
│   ├── main.py           # FastAPI application entry point
│   └── ...
├── docker-compose.yaml   # Docker Compose configuration for services
├── dockerfile            # Dockerfile for the FastAPI application
└── requirements.txt      # Python project dependencies
```

## Prerequisites

-   Docker and Docker Compose
-   An external OCR service compatible with the Ollama API, running on `http://localhost:11434`. The service should have the `scb10x/typhoon-ocr1.5-3b:latest` model available.
-   Poppler installed on the host machine. The service has a hardcoded path (`E:\poppler\poppler-25.12.0\Library\bin`) for Poppler, which you may need to adjust in `app/services/lc.py` to match your system.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Tanabordeee/autoship-hub-backend.git
cd autoship-hub-backend
```

### 2. Configure Environment Variables

Create a `.env` file in the root of the project and add the following configuration. Replace the placeholder values with your own.

```env
# A strong, secret string for signing JWTs
SECRET_KEY=your_super_secret_key

# The algorithm used for JWT signing
ALGORITHM=HS256

# The expiration time for access tokens in hours
ACCESS_TOKEN_EXPIRE_HOURS=24

# The connection string for the PostgreSQL database
DATABASE_URL=postgresql://postgres:password@postgres:5432/mydb
```

### 3. Run the Application

Start all services using Docker Compose. This will build the FastAPI application image and start containers for the app, a PostgreSQL database, and pgAdmin.

```bash
docker-compose up --build -d
```

The API will be available at `http://localhost:8000`.

### 4. Access Services

-   **API Documentation (Swagger UI):** `http://localhost:8000/docs`
-   **pgAdmin (Database GUI):** `http://localhost:5050`
    -   **Email:** `admin@admin.com`
    -   **Password:** `admin`

## API Endpoints

The API provides the following endpoints under the `/api/v1` prefix.

### Authentication

-   `POST /login`: Authenticate a user and receive a JWT access token.

### Users

-   `POST /users`: Register a new user (admin-only).
-   `GET /me`: Get the currently authenticated user's details.
-   `GET /admin`: An example admin-protected endpoint.

### Proforma Invoices

-   `POST /proforma_invoices`: Create a new proforma invoice.
-   `GET /proforma_invoices`: Retrieve a list of all proforma invoices.
-   `GET /proforma_invoices/pi_id/{pi_id}`: Get invoice details by its `pi_id`.
-   `GET /proforma_invoices/id/{id}`: Get invoice details by its database ID.
-   `POST /proforma_invoices/approve/{pi_id}`: Approve a proforma invoice.
-   `POST /proforma_invoices/reject/{pi_id}`: Reject a proforma invoice.
-   `GET /proforma_invoices/{pi_id}/pdf`: Generate and download a PDF version of the invoice.

### Letter of Credit (LC)

-   `POST /extract-lc`: Upload a PDF file to extract LC data using OCR.
-   `POST /create-lc`: Create a new LC record from extracted or provided data.
