from datetime import datetime, timezone, timedelta
from typing import Optional
import hashlib
import jwt
from passlib.context import CryptContext
from app.config.settings import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def _pre_hash(password: str) -> str:
        """
        SHA-256 pre-hash before bcrypt to safely handle passwords > 72 bytes.
        bcrypt silently truncates or raises ValueError on passwords longer than 72 bytes.
        SHA-256 produces a 64-char hex string — always under bcrypt's limit.
        """
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(AuthService._pre_hash(password))

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(AuthService._pre_hash(plain_password), hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def decode_access_token(token: str) -> dict:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except jwt.PyJWTError:
            from app.features.auth.exceptions import InvalidCredentialsException
            raise InvalidCredentialsException("Could not validate credentials.")
