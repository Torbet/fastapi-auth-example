from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import select

from app.core.dependencies import CurrentUser, Session
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, response: Response, session: Session):
    user = await session.scalar(select(User).where(User.email == body.email))
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id)
    response.set_cookie(key="token", value=token, httponly=True, samesite="lax")
    return user


@router.post("/signup", response_model=RegisterResponse)
async def signup(body: RegisterRequest, response: Response, session: Session):
    existing = await session.scalar(select(User).where(User.email == body.email))
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(
        name=body.name,
        email=body.email,
        hashed_password=hash_password(body.password),
    )
    session.add(user)
    await session.commit()
    token = create_access_token(user.id)
    response.set_cookie(key="token", value=token, httponly=True, samesite="lax")
    return user


@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie(key="token", httponly=True, samesite="lax")


@router.get("/me", response_model=UserRead)
async def me(current_user: CurrentUser):
    return current_user
