from pydantic import BaseModel, HttpUrl
from enum import Enum


class URLType(str, Enum):
    public = "public"
    private = "private"


class URLBase(BaseModel):
    target_url: HttpUrl
    type: URLType = URLType.public


class UserSchema(BaseModel):
    id: int
    username: str
    token: str
    is_active: bool

    class Config:
        orm_mode = True
