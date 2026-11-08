from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session
    
from app.config import settings
from app.database import get_db
    
# OAuth2 scheme: expects the frontend to send "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)
    
    
def get_current_user_payload(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Extracts and decodes the JWT token from the Authorization header.
    Returns the token payload (e.g., {'sub': 'user_id_123', 'exp': ...}).
    Raises HTTP 401 Unauthorized if the token is missing, invalid, or expired.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )