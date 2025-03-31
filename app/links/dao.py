from sqlalchemy import update, event, delete
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.dao.base import BaseDAO
from app.links.models import Link
from app.database import async_session_maker


class LinksDAO(BaseDAO):
    model = Link

