from fastapi import FastAPI
from app.users.router import router as router_users
from app.links.router import router as router_links
from datetime import datetime, timezone
import asyncio
from app.links.dao import LinksDAO
from sqlalchemy.exc import OperationalError
from app.database import async_session_maker
from sqlalchemy import text

app = FastAPI()

async def wait_for_db():
    max_attempts = 10
    attempt = 0
    while attempt < max_attempts:
        try:
            async with async_session_maker() as session:
                await session.execute(text("SELECT 1"))
                return True
        except OperationalError:
            attempt += 1
            await asyncio.sleep(2)
    raise Exception("БД не готова")


async def delete_expired_links():
    while True:
        try:
            now = datetime.now(timezone.utc)
            print(f"\n[Удаление ссылок] Текущее время (UTC): {now}")

            links = await LinksDAO.find_all()
            print(f"Найдено ссылок всего: {len(links)}")

            expired_count = 0
            for link in links:
                if link.expires_at is not None:
                    expires_at = (
                        link.expires_at.replace(tzinfo=timezone.utc)
                        if link.expires_at.tzinfo is None
                        else link.expires_at.astimezone(timezone.utc)
                    )

                    print(f"Проверка ссылки {link.short_URL}: "
                          f"expires_at={expires_at} (UTC)")

                    if expires_at <= now:
                        print(f"Ссылка {link.short_URL} протухла! Удаляем...")
                        try:
                            await LinksDAO.delete(short_URL=link.short_URL)
                            expired_count += 1
                            print(f"Успешно удалено!")
                        except Exception as e:
                            print(f"Ошибка удаления: {str(e)}")

            print(f"Удалено просроченных ссылок: {expired_count}")
            await asyncio.sleep(60)

        except Exception as e:
            print(f"КРИТИЧЕСКАЯ ОШИБКА: {str(e)}", exc_info=True)
            await asyncio.sleep(10)





@app.on_event("startup")
async def startup_event():
    try:
        await wait_for_db()
        asyncio.create_task(delete_expired_links())
    except Exception as e:
        print(f"Ошибка при запуске: {e}")
        raise

app.include_router(router_users)
app.include_router(router_links)