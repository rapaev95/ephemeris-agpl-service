"""API v1 router aggregator."""

from fastapi import APIRouter
from app.api import routes_meta, routes_positions, routes_houses, routes_design_time

router = APIRouter()

# Include all v1 routes
router.include_router(routes_meta.router)
router.include_router(routes_positions.router)
router.include_router(routes_houses.router)
router.include_router(routes_design_time.router)
