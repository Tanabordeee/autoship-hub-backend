from fastapi import APIRouter
from app.api.v1.endpoints import users
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import proforma_invoices

api_router = APIRouter()
api_router.include_router(users.router, tags=["users"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(proforma_invoices.router, tags=["proforma_invoices"])