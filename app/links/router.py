from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import RedirectResponse
from app.links.dao import LinksDAO
from app.links.rb import RBLink
from app.links.schemas import SLink, SLinkAdd, SLinkURL, SLinkAddURLtime, SLinkShortURL, SLinkStat
from app.links.coder import short_url
from typing import Dict, Optional
from jose import jwt, JWTError
from datetime import datetime, timezone
from app.config import get_auth_data
from app.users.dao import UsersDAO
from app.users.models import User
from fastapi.security import APIKeyCookie

def get_token(request: Request):
    token = request.cookies.get('users_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    return token

cookie_scheme = APIKeyCookie(name="users_access_token", auto_error=False)



async def get_current_user(token: Optional[str] = Depends(cookie_scheme)):
    if not token:
        return None
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=auth_data['algorithm'])
    except:
        return None


    expire: str = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        return None  #TokenExpiredException

    user_id: str = payload.get('sub')
    if not user_id:
        return None   #NoUserIdException

    user = await UsersDAO.find_one_or_none_by_id(int(user_id))
    if not user:
        return None
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        return current_user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Недостаточно прав!!!')#ForbiddenException




router = APIRouter(prefix='/links', tags=['API-сервис сокращения ссылок'])



@router.get("/", summary="Получить все зарегистрированные ссылки")
async def get_all_links(request_body: RBLink = Depends()) -> list[SLink]:
    """
    Получить все зарегистрированные ссылки, сохранённые в базе данных.
    """
    return await LinksDAO.find_all(**request_body.to_dict())


@router.post("/shorten", summary="Сгенирировать короткую ссылку")
async def add_link(link: SLinkAddURLtime, user_data: Optional[User] = Depends(get_current_user)) -> dict:
    """
    Пользователь отправляет запрос (POST /links/shorten) с длинной ссылкой.
    Сервис генерирует уникальный короткий код и возвращает его пользователю.

    Указание времени жизни ссылки (опционально):
    POST /links/shorten (создается с параметром expires_at в формате даты с точностью до минуты).
    После указанного времени короткая ссылка автоматически удаляется.

    Указание уникального alias (опционально):
    POST /links/shorten создается с параметром alias по желанию пользователя.
    """
    check_url = await LinksDAO.find_one_or_none(original_URL = link.original_URL)

    if check_url is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f'В сервисе уже есть короткая ссылка для {link.original_URL}')

    if link.alias:
        if await LinksDAO.find_one_or_none(short_URL=link.alias):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Короткая ссылка {link.alias} уже используется в сервисе')
        else:
            short_URL=link.alias
    else:
        short_URL = short_url(link.original_URL)
        counter = 0
        while await LinksDAO.find_one_or_none(short_URL = short_URL):
            short_URL = short_url(link.original_URL)
            counter+=1
            if counter == 2000:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                              detail=f'Сервис не может сгенерировать короткую ссылку для {link.original_URL}')

    if user_data:
        is_registered = True
        id_user = user_data.id
    else:
        is_registered = False
        id_user = None

    link = SLinkAdd(**link.model_dump(), short_URL = short_URL, clicks = 0, is_registered = is_registered, id_user = id_user)
    #print(link)
    check = await LinksDAO.add(**link.dict())
    if check:
        return {"message": "Сcылка успешно добавлена!", "link": link}
    else:
        return {"message": "Ошибка при добавлении ссылки!"}




@router.get("/search", summary="Поиск ссылки по оригинальному URL")
async def search_link(url: str) -> SLink:
    """
    Поиск ссылки по оригинальному URL:
    GET /links/search?original_url={url}
    """
    original_URL=SLinkURL(original_URL=url).original_URL
    link = await LinksDAO.find_one_or_none(original_URL=original_URL)
    print(link)

    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{url} не зарегистрирован в сервисе!"
        )
    return link



@router.get("/{short_code}", summary="Воспользоваться короткой ссылкой")
async def redirect_to_original_url(short_code: str):
    """
    При открытии короткой ссылки (GET-запрос к /{short_code}) сервис ищет в базе данных соответствующий оригинальный URL и перенаправляет пользователя (Redirect).
    """
    short_code = SLinkShortURL(short_URL=short_code).short_URL
    link = await LinksDAO.find_one_or_none(short_URL=short_code)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Короткая ссылка не найдена"
        )

    value = link.clicks+1
    await LinksDAO.update({'short_URL': short_code}, clicks=value)

    return RedirectResponse(url=link.original_URL, status_code=status.HTTP_302_FOUND)

"""
DELETE /links/{short_code} – удаляет связь.

Изменение и удаление ссылки доступно только зарегистрированным пользователям.
Авторские ссылки могут изменять или удалять только их авторы.
Ссылки, созданные неавторизованными пользователями, могут быть изменены или удалены любым пользователем.
"""

@router.delete("/{short_code}", summary="Удалить короткую ссылку")
async def delete_url(short_code: str, user_data: Optional[User] = Depends(get_current_user)):
    """
    DELETE /links/{short_code} – удаляет связь.

    Изменение и удаление ссылки доступно только зарегистрированным пользователям.
    Авторские ссылки могут изменять или удалять только их авторы.
    Ссылки, созданные неавторизованными пользователями, могут быть изменены или удалены любым пользователем.
    """
    short_code = SLinkShortURL(short_URL=short_code).short_URL
    link = await LinksDAO.find_one_or_none(short_URL=short_code)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Короткая ссылка не найдена"
        )

    if user_data:
        is_registered = True
        id_user = user_data.id
    else:
        is_registered = False
        id_user = None

    link_user = link.id_user
    link_user_is_registered = link.is_registered

    if link_user_is_registered:
        if is_registered:
            if id_user == link_user:
                await LinksDAO.delete(short_URL=short_code)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Авторскую ссылку может удалить только ей автор!")
    else:
        await LinksDAO.delete(short_URL=short_code)




@router.put("/{short_code}", summary="Заменить длинную ссылку по короткой ссылке")
async def update_url(short_code: str, url: SLinkURL, user_data: Optional[User] = Depends(get_current_user)):
    """
    PUT /links/{short_code} – обновляет URL (к короткой ссылке привязывается новая длинная ссылка).

    Изменение и удаление ссылки доступно только зарегистрированным пользователям.
    Авторские ссылки могут изменять или удалять только их авторы.
    Ссылки, созданные неавторизованными пользователями, могут быть изменены или удалены любым пользователем.
    """
    original_URL = url.original_URL
    short_code = SLinkShortURL(short_URL=short_code).short_URL
    link = await LinksDAO.find_one_or_none(short_URL=short_code)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Короткая ссылка не найдена"
        )
    if user_data:
        is_registered = True
        id_user = user_data.id
    else:
        is_registered = False
        id_user = None

    link_user = link.id_user
    link_user_is_registered = link.is_registered

    if link_user_is_registered:
        if is_registered:
            if id_user == link_user:
                await LinksDAO.update({'short_URL': short_code}, original_URL=original_URL)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Авторскую ссылку может удалить только ей автор!")
    else:
        await LinksDAO.update({'short_URL': short_code}, original_URL=original_URL)




@router.get("/{short_code}/stats", summary="Статистика по короткой ссылке")
async def stat_url(short_code: str) -> SLinkStat:
    """
    Статистика по ссылке:
    GET /links/{short_code}/stats
    Отображает оригинальный URL, возвращает дату создания, количество переходов, дату последнего использования.
    """
    short_code = SLinkShortURL(short_URL=short_code).short_URL
    link = await LinksDAO.find_one_or_none(short_URL=short_code)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Короткая ссылка не найдена"
        )

    return link








