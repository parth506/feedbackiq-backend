"""
Auth Router — Login, Register, Get Current User
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.features.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.features.auth.service import AuthService
from app.features.auth.dependencies import get_current_user
from app.database.session import get_database

router = APIRouter(prefix="/v1/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register a new user account and store in MongoDB."""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")

    # Check if email already registered
    existing = await db["users"].find_one({"email": request.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = AuthService.hash_password(request.password)
    user_doc = {
        "name": request.name,
        "email": request.email,
        "password": hashed_pw,
        "role": "admin",
        "organization": request.organization_name or "FeedbackIQ",
    }
    result = await db["users"].insert_one(user_doc)
    return UserResponse(
        id=str(result.inserted_id),
        name=request.name,
        email=request.email,
        role="admin",
        organization=user_doc["organization"],
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate credentials and return a JWT access token."""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")

    user = await db["users"].find_one({"email": request.email})
    if not user or not AuthService.verify_password(request.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = AuthService.create_access_token({
        "sub": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user.get("role", "admin"),
        "organization": user.get("organization", "FeedbackIQ"),
    })
    return TokenResponse(access_token=token, token_type="bearer", expires_in=1800)


@router.get("/me", response_model=UserResponse)
async def me(current_user: UserResponse = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return current_user
