from fastapi import APIRouter, Response, Depends


from app.users.auth import get_password_hash, authenticate_user, create_access_token
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user, get_current_admin_user
from app.users.models import User
from app.users.schemas import SUserRegister, SUserAuth

router = APIRouter(prefix='/auth', tags=['Авторизация пользователей'])


@router.post("/register/", summary="Регистрация пользователя")
async def register_user(user_data: SUserRegister) -> dict:
    user = await UsersDAO.find_one_or_none(email=user_data.email)
    if user:
        raise Exception("Существует пользователь с таким именем")
    user_dict = user_data.dict()
    user_dict['password'] = get_password_hash(user_data.password)
    await UsersDAO.add(**user_dict)
    return {'message': f'Вы успешно зарегистрированы!'}


@router.post("/login/", summary="Авторизация пользователя")
async def auth_user(response: Response, user_data: SUserAuth):
    check = await authenticate_user(email=user_data.email, password=user_data.password)
    if check is None:
        raise Exception("Неверный пароль или логин")     #IncorrectEmailOrPasswordException
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True,  max_age=36000,  samesite="lax")
    return {'ok': True, 'access_token': access_token, 'refresh_token': None, 'message': 'Авторизация успешна!'}



@router.post("/logout/", summary="Оключение авторизации")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}


@router.get("/me/", summary="Получить данные об авторизованном пользователе")
async def get_me(user_data: User = Depends(get_current_user)):
    return user_data


# вернёт список из всех пользователей только администратору

@router.get("/all_users/", summary="Получить данные обо всех зарегистрированных пользователях (только для админа)")
async def get_all_users(user_data: User = Depends(get_current_admin_user)):
    return await UsersDAO.find_all()
