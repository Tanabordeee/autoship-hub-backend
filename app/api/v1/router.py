from fastapi import APIRouter
from app.api.v1.endpoints import users
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import proforma_invoices
from app.api.v1.endpoints import lc
from app.api.v1.endpoints import booking
from app.api.v1.endpoints import vehicle_register
from app.api.v1.endpoints import si
from app.api.v1.endpoints import bl
from app.api.v1.endpoints import bv
from app.api.v1.endpoints import insurance
from app.api.v1.endpoints import commercial_invoice
from app.api.v1.endpoints import bencer
from app.api.v1.endpoints import transaction
from app.api.v1.endpoints import analytics

api_router = APIRouter()
api_router.include_router(users.router, tags=["users"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(proforma_invoices.router, tags=["proforma_invoices"])
api_router.include_router(lc.router, tags=["lc"])
api_router.include_router(booking.router, tags=["booking"])
api_router.include_router(vehicle_register.router, tags=["vehicle_register"])
api_router.include_router(si.router, tags=["si"])
api_router.include_router(bl.router, tags=["bl"])
api_router.include_router(bv.router, tags=["bv"])
api_router.include_router(insurance.router, tags=["insurance"])
api_router.include_router(commercial_invoice.router, tags=["commercial_invoice"])
api_router.include_router(bencer.router, tags=["bencer"])
api_router.include_router(transaction.router, tags=["transaction"])
api_router.include_router(analytics.router, tags=["analytics"])
