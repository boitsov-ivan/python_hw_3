from datetime import datetime, date, timezone
from typing import Optional
import re
from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict


class SLink(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., ge=1, description="ID ссылки")
    original_URL: str = Field(..., min_length=1, max_length=200, description="Длинная ссылка, от 1 до 200 символов")
    short_URL: str = Field(..., min_length=1, max_length=30, description="Короткая ссылка, от 1 до 30 символов")
    clicks: int = Field(..., ge=0, description="Количество переходов по ссылке")
    #expires_at: Optional[datetime] = Field(None, description="Время жизни ссылки")
    expires_at: datetime | None = None
    is_registered: bool = Field(..., description="Наличие регистрации автора ссылки в сервисе")
    id_user: Optional[int] = Field(None, ge=1, description="ID автора ссылки")
    
    @field_validator('expires_at', mode='before')
    @classmethod
    def convert_to_utc(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class SLinkURL(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_URL: str = Field(..., min_length=1, max_length=200, description="Длинная ссылка, от 1 до 200 символов")


class SLinkShortURL(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    short_URL: str = Field(..., min_length=1, max_length=30, description="Короткая ссылка, от 1 до 30 символов")




class SLinkAddURLtime(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_URL: str = Field(..., min_length=1, max_length=200, description="Длинная ссылка, от 1 до 200 символов")
    alias: Optional[str] = Field(None, min_length=1, max_length=30, description="Короткая ссылка, от 1 до 30 символов")
    #expires_at: Optional[datetime] = Field(None, description="Время жизни ссылки")
    expires_at: datetime | None = None



    


class SLinkAdd(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_URL: str = Field(..., min_length=1, max_length=200, description="Длинная ссылка, от 1 до 200 символов")
    short_URL: str = Field(..., min_length=1, max_length=30, description="Короткая ссылка, от 1 до 30 символов")
    clicks: int = Field(..., ge=0, description="Количество переходов по ссылке")
    #expires_at: Optional[datetime] = Field(None, description="Время жизни ссылки")
    expires_at: datetime | None = None
    is_registered: bool = Field(..., description="Наличие регистрации автора ссылки в сервисе")
    id_user: Optional[int] = Field(None, ge=1, description="ID автора ссылки")

    @field_validator('expires_at', mode='before')
    @classmethod
    def convert_to_utc(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class SLinkUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_URL: str = Field(..., min_length=1, max_length=200, description="Длинная ссылка, от 1 до 200 символов")
    short_URL: str = Field(..., min_length=1, max_length=30, description="Короткая ссылка, от 1 до 30 символов")
    clicks: int = Field(..., ge=0, description="Количество переходов по ссылке")
    #expires_at: datetime = Field(..., description="Время жизни ссылки")
    expires_at: datetime | None = None
    is_registered: bool = Field(..., description="Наличие регистрации автора ссылки в сервисе")
    id_user: int = Field(..., ge=1, description="ID автора ссылки")

    @field_validator('expires_at', mode='before')
    @classmethod
    def convert_to_utc(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class SLinkStat(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_URL: str = Field(..., min_length=1, max_length=200, description="Длинная ссылка, от 1 до 200 символов")
    short_URL: str = Field(..., min_length=1, max_length=30, description="Короткая ссылка, от 1 до 30 символов")
    clicks: int = Field(..., ge=0, description="Количество переходов по ссылке")
    #expires_at: Optional[datetime] = Field(None, description="Время жизни ссылки")
    expires_at: datetime | None = None
    created_at: datetime = Field(..., description="Дата создания ссылки")
    updated_at: datetime = Field(..., description="Дата последнего использования ссылки")

    @field_validator('expires_at', mode='before')
    @classmethod
    def convert_to_utc(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
