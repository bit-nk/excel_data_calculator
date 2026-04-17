"""Shared API dependencies — auth, DB session, RBAC."""

import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.users import User
from app.models.enums import UserRole

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise _CREDENTIALS_EXCEPTION

    user_id_raw = payload.get("sub")
    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError):
        logger.warning("JWT token contained non-integer sub claim: %s", type(user_id_raw).__name__)
        raise _CREDENTIALS_EXCEPTION

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise _CREDENTIALS_EXCEPTION

    return user


def require_role(*roles: UserRole):
    """Dependency factory that checks user has one of the required roles."""

    async def checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        await db.refresh(current_user, ["role"])
        if current_user.role.name not in [r.value for r in roles]:
            logger.warning(
                "Access denied for user_id=%s role=%s, required=%s",
                current_user.id, current_user.role.name, [r.value for r in roles],
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return checker


_PERMISSION_FIELDS = {
    "view_all_bus": "can_view_all_bus",
    "approve_reports": "can_approve_reports",
    "manage_rules": "can_manage_rules",
    "export_ledger": "can_export_ledger",
}


def require_permission(permission: str):
    """Dependency factory that checks the user's role grants a specific permission flag."""

    field = _PERMISSION_FIELDS.get(permission)
    if field is None:
        raise ValueError(f"Unknown permission: {permission}")

    async def checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        await db.refresh(current_user, ["role"])
        if not getattr(current_user.role, field, False):
            logger.warning(
                "Permission denied: user_id=%s role=%s missing=%s",
                current_user.id, current_user.role.name, permission,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return checker
