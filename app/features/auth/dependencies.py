from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.features.auth.service import AuthService
from app.features.auth.schemas import UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=True)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """Decode JWT and return the authenticated user. Raises 401 if invalid."""
    try:
        payload = AuthService.decode_access_token(token)
        return UserResponse(
            id=payload.get("sub", ""),
            name=payload.get("name", ""),
            email=payload.get("email", ""),
            role=payload.get("role", "admin"),
            organization=payload.get("organization", "FeedbackIQ"),
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
