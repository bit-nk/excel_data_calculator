import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_password_constant_time, create_access_token
from app.models.users import User
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(request_body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"

    result = await db.execute(select(User).where(User.email == request_body.email))
    user = result.scalar_one_or_none()

    # Constant-time password check — runs bcrypt even if user doesn't exist
    hashed = user.hashed_password if user else None
    password_valid = verify_password_constant_time(request_body.password, hashed)

    if not user or not password_valid:
        logger.warning("Failed login attempt for email=%s from ip=%s", request_body.email, client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        logger.warning("Login attempt on disabled account email=%s from ip=%s", request_body.email, client_ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    logger.info("Successful login for user_id=%s from ip=%s", user.id, client_ip)
    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.refresh(current_user, ["role"])
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role_name=current_user.role.name,
        business_unit_id=current_user.business_unit_id,
        is_active=current_user.is_active,
    )
