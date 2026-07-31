from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="admin@feedbackiq.ai")
    password: str = Field(..., min_length=6, example="SecurePassword123!")

class RegisterRequest(BaseModel):
    name: str = Field(..., example="Enterprise Admin")
    email: EmailStr = Field(..., example="admin@feedbackiq.ai")
    password: str = Field(..., min_length=6, example="SecurePassword123!")
    organization_name: Optional[str] = Field(default="FeedbackIQ Global", example="FeedbackIQ Global")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: str = "admin"
    organization: str = "FeedbackIQ Global"
