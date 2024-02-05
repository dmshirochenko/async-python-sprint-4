from typing import Optional, List

import validators
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from src.services.url_services import create_db_url, fetch_user_links, get_db_url_by_key, deactivate_db_url_by_key
from src.db.db_connector import get_async_session
from src.models.models import User
from src.models.schemas import URLBase, LinkResponse, URLResponse

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


@router.get("/v1/ping")
async def ping_database(db: AsyncSession = Depends(get_async_session)):
    try:
        await db.execute(select(1))
        return {"message": "Database is reachable"}
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database is not reachable")


@router.post("/v1/url", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
async def create_url(
    url: URLBase, db: AsyncSession = Depends(get_async_session), token: str = Depends(token_dependency)
):
    if not validators.url(url.target_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Your provided URL is not valid")

    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized or user not found")

    db_url = await create_db_url(db=db, url=url, user_id=user.id)
    return {"key": db_url.key, "short_url": db_url.short_url, "target_url": db_url.target_url}


@router.delete("/v1/url/{key}")
async def delete_url(key: str, db: AsyncSession = Depends(get_async_session), token: str = Depends(token_dependency)):
    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized or user not found")

    deactivation_result = await deactivate_db_url_by_key(db, key, user.id)
    if not deactivation_result:
        raise HTTPException(status_code=404, detail="URL not found or you don't have permission to delete it")

    return JSONResponse(content={"message": "Link has been successfully deactivated"}, status_code=status.HTTP_200_OK)


@router.get("/v1/user/status", response_model=List[LinkResponse])
async def get_user_links(db: AsyncSession = Depends(get_async_session), token: str = Depends(token_dependency)):
    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized or user not found")

    formatted_links = await fetch_user_links(db, user.id)

    return formatted_links


@router.get("/r/{key}")
async def redirect_to_url(request: Request, key: str, db: AsyncSession = Depends(get_async_session)):
    url = await get_db_url_by_key(db, key)

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    authorization: str = request.headers.get("Authorization")
    token = authorization.split(" ")[1] if authorization and authorization.startswith("Bearer ") else None

    if url.type == "private":
        if not token:
            raise HTTPException(status_code=401, detail="Authorization required for private URLs")

        user = await get_user_by_token(db, token)
        if not user or user.id != url.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this URL")

    return Response(status_code=307, headers={"Location": url.target_url})
