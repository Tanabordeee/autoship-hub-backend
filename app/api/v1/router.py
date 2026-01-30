from fastapi import APIRouter
from app.api.v1.endpoints import users
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import proforma_invoices
from app.api.v1.endpoints import lc
from app.api.v1.endpoints import booking
from app.api.v1.endpoints import vehicle_register
from app.api.v1.endpoints import si
from app.api.v1.endpoints import bl

api_router = APIRouter()
api_router.include_router(users.router, tags=["users"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(proforma_invoices.router, tags=["proforma_invoices"])
api_router.include_router(lc.router, tags=["lc"])
api_router.include_router(booking.router, tags=["booking"])
api_router.include_router(vehicle_register.router, tags=["vehicle_register"])
api_router.include_router(si.router, tags=["si"])
api_router.include_router(bl.router, tags=["bl"])
