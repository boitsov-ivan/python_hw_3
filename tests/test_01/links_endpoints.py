import links.router
import pytest


from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.main import app
from app.links.schemas import SLinkAddURLtime, SLinkURL, SLinkShortURL
from app.users.models import User
from app.links.models import Link

client = TestClient(app)





def test_get_all_links(mocker):
    mock_links = [
        {"id": 1, "original_URL": "https://example.com", "short_URL": "abc123"},
        {"id": 2, "original_URL": "https://example.org", "short_URL": "def456"}
    ]
    mocker.patch("app.links.dao.LinksDAO.find_all", return_value=mock_links)
    
    response = client.get("/links/")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["short_URL"] == "abc123"









@pytest.fixture
def test_user():
    return User(
        id=1,
        phone_number="+1234567890",
        first_name="Test",
        last_name="User",
        email="test@example.com",
        password="hashedpassword",
        is_admin=False
    )

@pytest.fixture
def test_link():
    return Link(
        id=1,
        original_URL="https://example.com",
        short_URL="abc123",
        clicks=5,
        is_registered=True,
        id_user=1,
        created_at=datetime.now() - timedelta(days=1),
        updated_at=datetime.now()
    )

@pytest.fixture
def test_link_unregistered():
    return Link(
        id=2,
        original_URL="https://unregistered.com",
        short_URL="def456",
        clicks=0,
        is_registered=False,
        id_user=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

# Тесты для эндпоинтов
def test_get_all_links(mocker, test_link):
    # Мокируем зависимость
    mock_find_all = mocker.patch(
        "app.links.dao.LinksDAO.find_all",
        return_value=[test_link]
    )
    
    response = client.get("/links/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["short_URL"] == "abc123"
    mock_find_all.assert_called_once()

def test_add_link_success(mocker):
    test_data = {
        "original_URL": "https://new.com",
        "alias": None,
        "expires_at": None
    }
    
    # Мокируем зависимости
    mocker.patch(
        "app.links.dao.LinksDAO.find_one_or_none",
        return_value=None
    )
    mock_add = mocker.patch(
        "app.links.dao.LinksDAO.add",
        return_value=True
    )
    
    response = client.post("/links/shorten", json=test_data)
    assert response.status_code == 200
    assert "Сcылка успешно добавлена!" in response.json()["message"]
    mock_add.assert_called_once()

def test_add_link_duplicate_url(mocker, test_link):
    test_data = {
        "original_URL": "https://example.com",
        "alias": None,
        "expires_at": None
    }
    

    mocker.patch(
        "app.links.dao.LinksDAO.find_one_or_none",
        return_value=test_link
    )
    
    response = client.post("/links/shorten", json=test_data)
    assert response.status_code == 401
    assert "уже есть короткая ссылка" in response.json()["detail"]

def test_add_link_duplicate_alias(mocker, test_link):
    test_data = {
        "original_URL": "https://new.com",
        "alias": "abc123",
        "expires_at": None
    }
    
  
    mocker.patch(
        "app.links.dao.LinksDAO.find_one_or_none",
        side_effect=[None, test_link]  
    )
    
    response = client.post("/links/shorten", json=test_data)
    assert response.status_code == 401
    assert "уже используется в сервисе" in response.json()["detail"]

def test_search_link_found(mocker, test_link):
    # Мокируем поиск ссылки
    mocker.patch(
        "app.links.dao.LinksDAO.find_one_or_none",
        return_value=test_link
    )
    
    response = client.get("/links/search", params={"url": "https://example.com"})
    assert response.status_code == 200
    assert response.json()["short_URL"] == "abc123"

def test_search_link_not_found(mocker):
    # Мокируем отсутствие ссылки
    mocker.patch(
        "app.links.dao.LinksDAO.find_one_or_none",
        return_value=None
    )
    
    response = client.get("/links/search", params={"url": "https://notfound.com"})
    assert response.status_code == 404
    assert "не зарегистрирован в сервисе" in response.json()["detail"]

def test_redirect_success(mocker, test_link):
    # Мокируем поиск ссылки и обновление счетчика
    mocker.patch(
        "app.links.dao.LinksDAO.find_one_or_none",
        return_value=test_link
    )
    mock_update = mocker.patch(
        "app.links.dao.LinksDAO.update",
        return_value=None
    )
    
    response = client.get("/links/abc123", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com"
    mock_update.assert_called_once()

def test_redirect_not_found(mocker):
    # Мокируем отсутствие ссылки
    mocker.patch(
        "app.links.dao.LinksDAO.find_one_or_none",
        return_value=None
    )
    
    response = client.get("/links/notfound")
    assert response.status_code == 404
    assert "Короткая ссылка не найдена" in response.json()["detail"]

def test_delete_link_authorized_owner(mocker, test_link, test_user):
    # Мокируем зависимости
    mocker.patch(
        "app.links.dao.LinksDAO.find_one_or_none",
        return_value=test_link
    )
    mock_delete = mocker.patch(
        "app.links.dao.LinksDAO.delete",
        return_value=None
    )
    mocker.patch(
        "app.users.dao.UsersDAO.find_one_or_none_by_id",
        return_value=test_user
    )
    
    # Создаем тестовый токен (в реальном приложении используйте ваш механизм аутентификации)
    test_token = "test_token"
    
    response = client.delete(
        "/links/abc123",
        cookies={"users_access_token": test_token}
    )
    assert response.status_code == 200
    mock_delete.assert_called_once()

def test_delete_link_unauthorized(mocker, test_link):
    # Мокируем ссылку, созданную зарегистрированным пользователем
    mocker.patch(
        "app.links.dao.LinksDAO.find_one_or_none",
        return_value=test_link
    )
    # Пользователь не авторизован
    mocker.patch(
        "app.users.dao.UsersDAO.find_one_or_none_by_id",
        return_value=None
    )
    
    response = client.delete("/links/abc123")
    assert response.status_code == 404
    assert "Авторскую ссылку может удалить только ей автор" in response.json()["detail"]

def test_delete_unregistered_link(mocker, test_link_unregistered):
    # Мокируем незарегистрированную ссылку
    mocker.patch(
        "app.links.dao.LinksDAO.find_one_or_none",
        return_value=test_link_unregistered
    )
    mock_delete = mocker.patch(
        "app.links.dao.LinksDAO.delete",
        return_value=None
    )
    
    response = client.delete("/links/def456")
    assert response.status_code == 200
    mock_delete.assert_called_once()

def test_update_link_success(mocker, test_link, test_user):
    update_data = {"original_URL": "https://updated.com"}
    
    # Мокируем зависимости
    mocker.patch(
        "app.links.dao.LinksDAO.find_one_or_none",
        return_value=test_link
    )
    mock_update = mocker.patch(
        "app.links.dao.LinksDAO.update",
        return_value=None
    )
    mocker.patch(
        "app.users.dao.UsersDAO.find_one_or_none_by_id",
        return_value=test_user
    )
    
    test_token = "test_token"
    
    response = client.put(
        "/links/abc123",
        json=update_data,
        cookies={"users_access_token": test_token}
    )
    assert response.status_code == 200
    mock_update.assert_called_once()

def test_get_link_stats(mocker, test_link):
    # Мокируем поиск ссылки
    mocker.patch(
        "app.links.dao.LinksDAO.find_one_or_none",
        return_value=test_link
    )
    
    response = client.get("/links/abc123/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["short_URL"] == "abc123"
    assert data["original_URL"] == "https://example.com"
    assert data["clicks"] == 5









def test_add_link_with_alias(mocker):
    test_data = {
        "original_URL": "https://alias.com",
        "alias": "myalias",
        "expires_at": None
    }
    
    mocker.patch("app.links.dao.LinksDAO.find_one_or_none", return_value=None)
    mocker.patch("app.links.dao.LinksDAO.add", return_value=True)
    
    response = client.post("/links/shorten", json=test_data)
    assert response.status_code == 200
    assert response.json()["link"]["short_URL"] == "myalias"

def test_add_link_with_expiration(mocker):
    expires_at = (datetime.now() + timedelta(days=7)).isoformat()
    test_data = {
        "original_URL": "https://expiring.com",
        "alias": None,
        "expires_at": expires_at
    }
    
    mocker.patch("app.links.dao.LinksDAO.find_one_or_none", return_value=None)
    mocker.patch("app.links.dao.LinksDAO.add", return_value=True)
    
    response = client.post("/links/shorten", json=test_data)
    assert response.status_code == 200
    assert "expires_at" in response.json()["link"]





def test_add_link_success(mocker):
    test_data = {
        "original_URL": "https://new.com",
        "alias": None,
        "expires_at": None
    }
    mocker.patch("app.links.dao.LinksDAO.find_one_or_none", return_value=None)
    mocker.patch("app.links.dao.LinksDAO.add", return_value=True)
    
    response = client.post("/links/shorten", json=test_data)
    assert response.status_code == 200
    assert "Сcылка успешно добавлена!" in response.json()["message"]

def test_add_link_with_alias(mocker):
    test_data = {
        "original_URL": "https://alias.com",
        "alias": "myalias",
        "expires_at": None
    }
    mocker.patch("app.links.dao.LinksDAO.find_one_or_none", return_value=None)
    mocker.patch("app.links.dao.LinksDAO.add", return_value=True)
    
    response = client.post("/links/shorten", json=test_data)
    assert response.status_code == 200
    assert response.json()["link"]["short_URL"] == "myalias"

def test_add_link_duplicate_url(mocker):
    test_data = {"original_URL": "https://duplicate.com"}
    mocker.patch("app.links.dao.LinksDAO.find_one_or_none", return_value={"short_URL": "exist123"})
    
    response = client.post("/links/shorten", json=test_data)
    assert response.status_code == 401
    assert "уже есть короткая ссылка" in response.json()["detail"]

def test_add_link_duplicate_alias(mocker):
    test_data = {"original_URL": "https://new.com", "alias": "taken"}
    mocker.patch("app.links.dao.LinksDAO.find_one_or_none", side_effect=[None, {"short_URL": "taken"}])
    
    response = client.post("/links/shorten", json=test_data)
    assert response.status_code == 401
    assert "уже используется в сервисе" in response.json()["detail"]




# tests/test_links_router.py
@pytest.mark.asyncio
async def test_update_link_unauthenticated(mocker, client):
    mocker.patch("app.links.dao.LinksDAO.find_one_or_none", return_value={
        "short_URL": "test123", 
        "is_registered": True,
        "id_user": 1
    })
    mocker.patch("app.users.dependencies.get_current_user", return_value=None)
    
    response = client.put("/links/test123", json={"original_URL": "https://new.com"})
    assert response.status_code == 404






@pytest.mark.asyncio
async def test_get_all_links_filtered(client, mocker):
    mock_links = [{"id": 1, "short_URL": "test123"}]
    mocker.patch("app.links.dao.LinksDAO.find_all", return_value=mock_links)
    
    response = client.get("/links/?short_URL=test123")
    assert response.status_code == 200
    assert response.json()[0]["short_URL"] == "test123"

@pytest.mark.asyncio
async def test_add_link_with_expiration(client, mocker):
    mocker.patch("app.links.dao.LinksDAO.find_one_or_none", return_value=None)
    mocker.patch("app.links.dao.LinksDAO.add", return_value=True)
    
    expires_at = (datetime.now() + timedelta(days=1)).isoformat()
    response = client.post("/links/shorten", json={
        "original_URL": "https://expire.com",
        "expires_at": expires_at
    })
    assert response.status_code == 200








@pytest.mark.asyncio
async def test_get_all_links_filtered(client, mocker):
    mock_links = [{"id": 1, "short_URL": "test123"}]
    mocker.patch("app.links.dao.LinksDAO.find_all", return_value=mock_links)
    
    response = client.get("/links/?short_URL=test123")
    assert response.status_code == 200
    assert response.json()[0]["short_URL"] == "test123"

@pytest.mark.asyncio
async def test_add_link_with_expiration(client, mocker):
    mocker.patch("app.links.dao.LinksDAO.find_one_or_none", return_value=None)
    mocker.patch("app.links.dao.LinksDAO.add", return_value=True)
    
    expires_at = (datetime.now() + timedelta(days=1)).isoformat()
    response = client.post(
        "/links/shorten", 
        json={
            "original_URL": "https://expire.com",
            "expires_at": expires_at
        }
    )
    assert response.status_code == 200
    assert "expires_at" in response.json()["link"]




