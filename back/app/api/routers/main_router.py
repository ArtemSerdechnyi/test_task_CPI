from fastapi import APIRouter
from back.app.api.routers.health import health_router
from back.app.api.routers.cpi import cpi_router
from back.app.api.routers.valuation import valuation_router

router = APIRouter(prefix="/api")
router.include_router(health_router, tags=["health"])
router.include_router(cpi_router, prefix="/cpi", tags=["cpi"])
router.include_router(valuation_router, prefix="/valuation", tags=["valuation"])
