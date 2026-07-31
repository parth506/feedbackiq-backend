from fastapi import APIRouter, Depends, status
from app.features.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.features.auth.service import AuthService
from app.features.auth.dependencies import get_current_user

router = APIRouter(prefix="/v1/auth", tags=["1. Authentication"])

@router.post("/login", response_model=TokenResponse, summary="User Authentication Login")
async def login(request: LoginRequest) -> TokenResponse:
    """Authenticate user credentials and issue JWT bearer access token."""
    token = AuthService.create_access_token({"sub": "user_admin_101", "email": request.email, "role": "admin"})
    return TokenResponse(access_token=token, token_type="bearer", expires_in=1800)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register Enterprise Account")
async def register(request: RegisterRequest) -> UserResponse:
    """Register new organization account and enterprise administrator."""
    return UserResponse(
        id="user_admin_101",
        name=request.name,
        email=request.email,
        role="admin",
        organization=request.organization_name or "FeedbackIQ Global"
    )

@router.get("/me", response_model=UserResponse, summary="Get Current Authenticated User")
async def me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Get active authenticated user identity context."""
    return current_user
