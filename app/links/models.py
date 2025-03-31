from sqlalchemy import ForeignKey, text, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base, str_uniq, int_pk, str_null_true
from datetime import date, datetime
from typing import Optional
from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey


class Link(Base):
    id: Mapped[int_pk]
    original_URL: Mapped[str_uniq]
    short_URL: Mapped[str_uniq]
    clicks: Mapped[int]                  # количество переходов
    #expires_at: Mapped[Optional[datetime]]   # время жизни ссылки
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    is_registered: Mapped[bool]          # зарегистрирован ли пользователь
    id_user: Mapped[Optional[int]]       # id создателя ссылки

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"original_URL={self.original_URL!r},"
                f"short_URL={self.short_URL!r})")

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {
            "id": self.id,
            "original_URL": self.original_URL,
            "short_URL": self.short_URL,
            "clicks": self.clicks,
            "expires_at": self.expires_at,
            "is_registered": self.is_registered,
            "id_user": self.id_user,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
