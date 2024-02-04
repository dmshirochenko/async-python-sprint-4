from fastapi import HTTPException
from starlette.datastructures import URL
from src.core.config import settings
from src.models import models
from src.schemas import schemas

def get_admin_info(db_url: models.URL, url_path_for: callable) -> schemas.URLInfo:
    base_url = URL(settings.base_url)
    admin_endpoint = url_path_for("administration_info", secret_key=db_url.secret_key)  # Adjusted to dynamic function parameter
    db_url.url = str(base_url.replace(path=db_url.key))
    db_url.admin_url = str(base_url.replace(path=admin_endpoint))
    return db_url
