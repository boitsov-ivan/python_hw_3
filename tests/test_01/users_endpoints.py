import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.main import app
from app.users.models import User
from app.users.schemas import SUserRegister, SUserAuth

client = TestClient(app)

# Тесты для /auth/register/
@pytest.mark.asyncio
async def test_register_user_success(mocker):
    # Мокируем зависимости
    mocker.patch("app.users.dao.UsersDAO.find_one_or_none", return_value=None)
    mock_add = mocker.patch("app.users.dao.UsersDAO.add", return_value=None)
    
    test_data = {
        "email": "new@example.com",
        "password": "strongpassword",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+1234567890"
    }
    
    response = client.post("/auth/register/", json=test_data)
    assert response.status_code == 200
    assert "Вы успешно зарегистрированы" in response.json()["message"]
    mock_add.assert_called_once()

@pytest.mark.asyncio
async def test_register_existing_user(mocker):
    mocker.patch("app.users.dao.UsersDAO.find_one_or_none", return_value=User(id=1))
    
    test_data = {
        "email": "existing@example.com",
        "password": "password",
        "first_name": "Existing",
        "last_name": "User"
    }
    
    response = client.post("/auth/register/", json=test_data)
    assert response.status_code == 400
    assert "Существует пользователь с таким именем" in str(response.json()["detail"])

# Тесты для /auth/login/
@pytest.mark.asyncio
async def test_login_success(mocker):
    mock_user = User(id=1, email="test@example.com", password_hash="hashedpass")
    mocker.patch("app.users.auth.authenticate_user", return_value=mock_user)
    mocker.patch("app.users.auth.create_access_token", return_value="test.token")
    
    test_data = {"email": "test@example.com", "password": "correctpass"}
    response = client.post("/auth/login/", json=test_data)
    
    assert response.status_code == 200
    assert response.json()["access_token"] == "test.token"
    assert "users_access_token" in response.cookies

@pytest.mark.asyncio
async def test_login_invalid_credentials(mocker):
    mocker.patch("app.users.auth.authenticate_user", return_value=None)
    
    test_data = {"email": "wrong@example.com", "password": "wrongpass"}
    response = client.post("/auth/login/", json=test_data)
    
    assert response.status_code == 400
    assert "Неверный пароль или логин" in str(response.json()["detail"])

# Тесты для /auth/logout/
def test_logout_success():
    response = client.post("/auth/logout/")
    assert response.status_code == 200
    assert "users_access_token" not in response.cookies
    assert "Пользователь успешно вышел" in response.json()["message"]

# Тесты для /auth/me/
@pytest.mark.asyncio
async def test_get_me_authenticated(mocker):
    mock_user = User(id=1, email="me@example.com")
    mocker.patch("app.users.dependencies.get_current_user", return_value=mock_user)
    
    response = client.get("/auth/me/", cookies={"users_access_token": "valid.token"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"

@pytest.mark.asyncio
async def test_get_me_unauthenticated(mocker):
    mocker.patch("app.users.dependencies.get_current_user", return_value=None)
    
    response = client.get("/auth/me/")
    assert response.status_code == 401

# Тесты для /auth/all_users/
@pytest.mark.asyncio
async def test_get_all_users_as_admin(mocker):
    mock_users = [
        User(id=1, email="admin@example.com", is_admin=True),
        User(id=2, email="user@example.com", is_admin=False)
    ]
    mocker.patch("app.users.dependencies.get_current_admin_user", return_value=mock_users[0])
    mocker.patch("app.users.dao.UsersDAO.find_all", return_value=mock_users)
    
    response = client.get("/auth/all_users/", cookies={"users_access_token": "admin.token"})
    assert response.status_code == 200
    assert len(response.json()) == 2

@pytest.mark.asyncio
async def test_get_all_users_as_regular_user(mocker):
    mock_user = User(id=2, email="user@example.com", is_admin=False)
    mocker.patch("app.users.dependencies.get_current_admin_user", side_effect=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недостаточно прав!!!"
    ))
    
    response = client.get("/auth/all_users/", cookies={"users_access_token": "user.token"})
    assert response.status_code == 401
    assert "Недостаточно прав" in response.json()["detail"]

# Дополнительные тесты для edge cases
@pytest.mark.asyncio
async def test_register_invalid_data():
    invalid_data = {
        "email": "not-an-email",
        "password": "short",
        "first_name": "",
        "last_name": ""
    }
    response = client.post("/auth/register/", json=invalid_data)
    assert response.status_code == 422  # Unprocessable Entity

@pytest.mark.asyncio
async def test_login_missing_fields():
    response = client.post("/auth/login/", json={"email": "only@email.com"})
    assert response.status_code == 422

# Тесты для cookie параметров
@pytest.mark.asyncio
async def test_login_cookie_settings(mocker):
    mock_user = User(id=1, email="cookie@test.com")
    mocker.patch("app.users.auth.authenticate_user", return_value=mock_user)
    mocker.patch("app.users.auth.create_access_token", return_value="cookie.token")
    
    response = client.post("/auth/login/", json={"email": "cookie@test.com", "password": "test"})
    cookie = response.cookies["users_access_token"]
    assert cookie == "cookie.token"
    assert response.headers["set-cookie"].lower().count("httponly") > 0
    assert response.headers["set-cookie"].lower().count("samesite=lax") > 0

# Тесты для хеширования паролей
def test_password_hashing():
    from app.users.auth import get_password_hash, verify_password
    plain_password = "testpassword123"
    hashed = get_password_hash(plain_password)
    assert verify_password(plain_password, hashed)
    assert not verify_password("wrongpassword", hashed)

# Тесты для токенов
def test_token_creation_verification(mocker):
    from app.users.auth import create_access_token, get_auth_data
    from jose import jwt
    
    test_data = {"sub": "123"}
    token = create_access_token(test_data)
    
    auth_data = get_auth_data()
    decoded = jwt.decode(token, auth_data["secret_key"], algorithms=[auth_data["algorithm"]])
    assert decoded["sub"] == "123"






# tests/test_auth.py
def test_get_password_hash():
    from app.users.auth import get_password_hash, verify_password
    hashed = get_password_hash("test")
    assert verify_password("test", hashed)
    assert not verify_password("wrong", hashed)

@pytest.mark.asyncio
async def test_authenticate_user_success(mocker):
    from app.users.auth import authenticate_user
    mock_user = User(id=1, email="test@test.com", password_hash=get_password_hash("right"))
    mocker.patch("app.users.dao.UsersDAO.find_one_or_none", return_value=mock_user)
    
    user = await authenticate_user("test@test.com", "right")
    assert user.id == 1





# tests/test_01/test_auth.py
def test_password_hashing():
    from app.users.auth import get_password_hash, verify_password
    hashed = get_password_hash("testpass")
    assert verify_password("testpass", hashed)
    assert not verify_password("wrongpass", hashed)

@pytest.mark.asyncio
async def test_authenticate_user_success(mocker):
    from app.users.auth import authenticate_user
    mock_user = User(
        email="test@test.com", 
        password_hash=get_password_hash("rightpass")
    )
    mocker.patch("app.users.dao.UsersDAO.find_one_or_none", return_value=mock_user)
    
    user = await authenticate_user("test@test.com", "rightpass")
    assert user.email == "test@test.com"

@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(mocker):
    mocker.patch("app.users.dao.UsersDAO.find_one_or_none", return_value=None)
    user = await authenticate_user("nonexistent@test.com", "wrongpass")
    assert user is None

