from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import URL
from sqlalchemy.future import select

from src.db import keygen
from src.models.models import URL
from src.models.schemas import URLBase
from src.core.config import settings


async def create_db_url(db: AsyncSession, url: URLBase, user_id: Optional[int] = None) -> URL:
    key = keygen.create_random_key()
    short_url = f"{settings.base_url}/{key}"

    db_url = URL(
        target_url=url.target_url, key=key, short_url=short_url, is_active=True, user_id=user_id, type=url.type
    )

    db.add(db_url)
    await db.commit()
    await db.refresh(db_url)

    return db_url


async def fetch_user_links(db: AsyncSession, user_id: int) -> List[dict]:
    result = await db.execute(select(URL).filter(URL.user_id == user_id, URL.is_active == True))
    links = result.scalars().all()

    response = [
        {"key": link.key, "short_url": link.short_url, "original_url": link.target_url, "type": link.type}
        for link in links
    ]
    return response


async def get_db_url_by_key(db: AsyncSession, key: str):
    result = await db.execute(select(URL).filter(URL.key == key))
    url = result.scalars().first()
    return url


async def deactivate_db_url_by_key(db: AsyncSession, key: str, user_id: int):
    result = await db.execute(select(URL).filter(URL.key == key, URL.user_id == user_id))
    db_url = result.scalars().first()

    if db_url:
        db_url.is_active = False
        await db.commit()
        return {"message": "URL has been successfully deactivated"}
    else:
        return None
