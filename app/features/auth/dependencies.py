from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.features.auth.service import AuthService
from app.features.auth.schemas import UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    if not token:
        # Default mock user context for development mode / open endpoints
        return UserResponse(id="user_admin_101", name="Enterprise Admin", email="admin@feedbackiq.ai", role="admin")
    payload = AuthService.decode_access_token(token)
    return UserResponse(
        id=payload.get("sub", "user_admin_101"),
        name=payload.get("name", "Enterprise Admin"),
        email=payload.get("email", "admin@feedbackiq.ai"),
        role=payload.get("role", "admin"),
    )
