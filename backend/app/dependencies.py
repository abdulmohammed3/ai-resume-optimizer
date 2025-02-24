from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import get_settings
from .core.security import auth_handler
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()

# Settings dependency
def get_app_settings():
    return get_settings()

async def verify_auth_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Verify JWT token from Clerk.
    
    Args:
        credentials: Bearer token credentials
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException if token is invalid
    """
    try:
        return await auth_handler.verify_token(credentials.credentials)
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

async def get_current_user(
    user_info: dict = Depends(verify_auth_token)
) -> dict:
    """
    Get current authenticated user.
    
    Args:
        user_info: User information from verified token
        
    Returns:
        Dict containing user details
        
    Raises:
        HTTPException if user is not found or inactive
    """
    if not user_info or not user_info.get('user_id'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user"
        )
    return user_info

def check_roles(required_roles: list[str]):
    """
    Create a dependency that checks for required roles.
    
    Args:
        required_roles: List of role names required for access
        
    Returns:
        Dependency function that validates user roles
    """
    async def role_checker(
        user: dict = Depends(get_current_user)
    ) -> dict:
        user_roles = set(user.get('roles', []))
        if not (required_roles and any(role in user_roles for role in required_roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return role_checker

# Common role-based dependencies
require_admin = check_roles(["admin"])
require_premium = check_roles(["premium", "admin"])