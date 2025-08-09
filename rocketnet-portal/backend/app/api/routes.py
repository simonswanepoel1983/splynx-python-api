"""
Main API router
Combines all API endpoint modules
"""

from fastapi import APIRouter

from app.api.endpoints import auth, customer, billing, usage, packages, speedtest, retention

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(customer.router, prefix="/customer", tags=["customer"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(usage.router, prefix="/usage", tags=["usage"])
api_router.include_router(packages.router, prefix="/packages", tags=["packages"])
api_router.include_router(speedtest.router, prefix="/speedtest", tags=["speedtest"])
api_router.include_router(retention.router, prefix="/retention", tags=["retention"])