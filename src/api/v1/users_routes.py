import secrets
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.db.db_connector import get_async_session
from src.models.models import User
from src.models.schemas import UserSchema

router = APIRouter()


@router.post("/v1/user/registration", status_code=status.HTTP_201_CREATED, response_model=UserSchema)
async def register_user(*, db: AsyncSession = Depends(get_async_session), username: str = Body(..., embed=True)) -> Any:
    """
    Register a new user with a given username.
    """
    token = secrets.token_urlsafe(32)
    new_user = User(username=username, token=token)
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is already taken")
