"""Authentication and authorization utilities."""
from typing import Optional, Dict
import jwt
from jwt import PyJWTError
from fastapi import HTTPException, status
import httpx
import logging
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ClerkAuth:
    """Handle Clerk authentication and validation."""
    
    def __init__(self):
        self.settings = get_settings()
        self.jwks_url = "https://clerk.your-domain.com/.well-known/jwks.json"  # TODO: Configure in settings
        self._jwks = None
    
    async def _fetch_jwks(self) -> Dict:
        """Fetch JSON Web Key Set from Clerk."""
        if self._jwks is None:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.jwks_url)
                response.raise_for_status()
                self._jwks = response.json()
        return self._jwks
    
    async def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify a JWT token from Clerk.
        
        Args:
            token: JWT token string
            
        Returns:
            Dict containing user information if valid
            
        Raises:
            HTTPException if token is invalid
        """
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Fetch JWKS
            jwks = await self._fetch_jwks()
            
            # Get header without verification
            unverified_header = jwt.get_unverified_header(token)
            
            # Find the key
            rsa_key = {}
            for key in jwks['keys']:
                if key['kid'] == unverified_header['kid']:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'n': key['n'],
                        'e': key['e']
                    }
                    break
            
            if rsa_key:
                try:
                    # Verify token
                    payload = jwt.decode(
                        token,
                        rsa_key,
                        algorithms=['RS256'],
                        audience=self.settings.CLERK_AUDIENCE,
                        issuer=self.settings.CLERK_ISSUER
                    )
                    
                    return {
                        'user_id': payload['sub'],
                        'email': payload.get('email'),
                        'roles': payload.get('roles', []),
                        'metadata': payload.get('user_metadata', {})
                    }
                    
                except jwt.ExpiredSignatureError:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token has expired"
                    )
                except jwt.JWTClaimsError:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid claims"
                    )
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Invalid token: {str(e)}"
                    )
                    
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signing key"
            )
            
        except PyJWTError as e:
            logger.error(f"JWT validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )

# Instantiate auth handler
auth_handler = ClerkAuth()