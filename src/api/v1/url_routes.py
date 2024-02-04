from typing import Optional, List

import validators
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.services.url_services import create_db_url, fetch_user_links
from src.db.db_connector import get_async_session
from src.models.models import User
from src.models.schemas import URLBase, LinkResponse

router = APIRouter()


async def get_user_by_token(db: AsyncSession, token: str) -> Optional[User]:
    async with db as session:
        result = await session.execute(select(User).filter(User.token == token))
        user = result.scalars().first()
        return user


async def token_dependency(authorization: Optional[str] = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header is missing.")

    scheme, _, token = authorization.partition(" ")
    if not scheme or scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing Bearer token.")

    return token


@router.get("/v1/health")
async def read_root():
    return "Welcome to the URL shortener API :)"


@router.post("/url")
async def create_url(
    url: URLBase, db: AsyncSession = Depends(get_async_session), token: str = Depends(token_dependency)
):
    if not validators.url(url.target_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Your provided URL is not valid")

    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized or user not found")

    await create_db_url(db=db, url=url, user_id=user.id)
    return JSONResponse(content={"message": "Link has been successfully added"}, status_code=status.HTTP_201_CREATED)


@router.get("/user/status", response_model=List[LinkResponse])
async def get_user_links(db: AsyncSession = Depends(get_async_session), token: str = Depends(token_dependency)):
    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized or user not found")

    formatted_links = await fetch_user_links(db, user.id)

    return formatted_links
