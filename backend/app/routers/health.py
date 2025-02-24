from fastapi import APIRouter, Depends
from ..dependencies import get_app_settings
from ..config import Settings

router = APIRouter()

@router.get("")
async def health_check(settings: Settings = Depends(get_app_settings)):
    """
    Health check endpoint.
    Returns basic application information and status.
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "api_version": settings.API_V1_STR
    }