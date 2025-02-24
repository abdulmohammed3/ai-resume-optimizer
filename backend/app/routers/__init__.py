from fastapi import APIRouter
from . import health, resume

# Create main router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(resume.router, prefix="/resumes", tags=["resumes"])