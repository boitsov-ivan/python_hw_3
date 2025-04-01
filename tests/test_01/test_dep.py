from fastapi import HTTPException
from app.users.dependencies import get_current_user, get_current_admin_user
from app.users.models import User
import pytest

def test_get_current_user_valid_token(mocker):
    mock_decode = mocker.patch("jose.jwt.decode", return_value={"sub": "1", "exp": "1234567890"})
    mock_find_user = mocker.patch("app.users.dao.UsersDAO.find_one_or_none_by_id", 
                                return_value=User(id=1, is_admin=False))
    
    user = get_current_user(token="valid.token.here")
    assert user.id == 1
    assert user.is_admin is False

@pytest.mark.asyncio
async def test_get_current_admin_user_unauthorized():
    regular_user = User(id=2, is_admin=False)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin_user(current_user=regular_user)
    assert exc_info.value.status_code == 401


# tests/test_01/test_dep.py
@pytest.mark.asyncio
async def test_get_current_user_valid_token(mocker):
    mock_decode = mocker.patch("jose.jwt.decode", return_value={"sub": "1", "exp": "1234567890"})
    mock_find_user = mocker.patch("app.users.dao.UsersDAO.find_one_or_none_by_id",
                                return_value=User(id=1, is_admin=False))
    
    user = await get_current_user(token="valid.token.here")
    assert user.id == 1

@pytest.mark.asyncio
async def test_get_current_admin_user(mocker):
    admin_user = User(id=1, is_admin=True)
    result = await get_current_admin_user(current_user=admin_user)
    assert result == admin_user




@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mocker):
    mocker.patch("jose.jwt.decode", side_effect=JWTError("Invalid token"))
    user = await get_current_user(token="invalid.token")
    assert user is None

@pytest.mark.asyncio
async def test_get_current_user_expired_token(mocker):
    mocker.patch("jose.jwt.decode", return_value={"sub": "1", "exp": "123"})
    user = await get_current_user(token="expired.token")
    assert user is None
