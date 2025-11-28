from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.openapi.models import OAuthFlowPassword, OAuthFlows
from fastapi.security import OAuth2
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.models.user import User


class OAuth2Cookie(OAuth2):
    """Custom OAuth2 scheme that reads the access token from a cookie.

    FastAPI's built-in OAuth2PasswordBearer expects the token in the
    Authorization header; this variant instead uses a `token` cookie
    so that the browser can automatically send it with each request.
    """

    def __init__(self, tokenUrl: str):
        password = OAuthFlowPassword(tokenUrl=tokenUrl)
        flows = OAuthFlows(password=password)
        super().__init__(flows=flows)

    async def __call__(self, request: Request) -> str:
        # Read token from HTTP-only cookie instead of Authorization header
        token = request.cookies.get("token")
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return token


oauth2_scheme = OAuth2Cookie(tokenUrl="/auth/login")

# Argon2-based password hasher with sensible defaults.
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain-text password using Argon2."""
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plain-text password against a stored Argon2 hash."""
    return password_hash.verify(password, hashed)


def create_access_token(user_id: UUID) -> str:
    """Create a short-lived JWT access token for the given user.

    The token contains:
      - `sub`: user ID (UUID as string)
      - `exp`: expiration time (30 minutes from now, UTC)
      - `iat`: issued-at time (now, UTC)
    """
    now = datetime.now(timezone.utc)
    data = {"sub": str(user_id), "exp": now + timedelta(minutes=30), "iat": now}
    return jwt.encode(data, settings.jwt_secret, algorithm="HS256")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """Resolve the currently authenticated user from the JWT cookie.

    - Decodes and validates the JWT
    - Extracts the `sub` claim (user ID)
    - Loads the corresponding `User` from the database
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired token")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
