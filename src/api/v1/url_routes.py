import logging.config
from typing import Optional, List

import validators
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, OperationalError, TimeoutError, DatabaseError


from src.services.url_services import create_db_url, fetch_user_links, get_db_url_by_key, deactivate_db_url_by_key
from src.db.db_connector import get_async_session
from src.models.models import User
from src.models.schemas import URLBase, LinkResponse, URLResponse
from src.core.logger import LOGGING


logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


router = APIRouter()


async def get_user_by_token(db: AsyncSession, token: str) -> Optional[User]:
    try:
        result = await db.execute(select(User).filter(User.token == token))
        user = result.scalars().first()
        return user
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database error occurred")


async def token_dependency(authorization: Optional[str] = Header(None)) -> str:
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
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database connection error")
    except TimeoutError:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Database connection timed out")
    except DatabaseError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="General database error")
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")


@router.post("/v1/url", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
async def create_url(
    url: URLBase, db: AsyncSession = Depends(get_async_session), token: str = Depends(token_dependency)
):
    if not validators.url(url.target_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL provided")

    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized or user not found")

    try:
        db_url = await create_db_url(db=db, url=url, user_id=user.id)
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Failed to create URL")

    return {"key": db_url.key, "short_url": db_url.short_url, "target_url": db_url.target_url}


@router.delete("/v1/url/{key}")
async def delete_url(key: str, db: AsyncSession = Depends(get_async_session), token: str = Depends(token_dependency)):
    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized or user not found")

    try:
        deactivation_result = await deactivate_db_url_by_key(db, key, user.id)
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Failed to deactivate URL")

    if not deactivation_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found or unauthorized to delete")

    return {"message": "URL successfully deactivated"}


@router.get("/v1/user/status", response_model=List[LinkResponse])
async def get_user_links(db: AsyncSession = Depends(get_async_session), token: str = Depends(token_dependency)):
    user = await get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized or user not found")

    try:
        links = await fetch_user_links(db, user.id)
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Failed to fetch user links")

    return links


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
