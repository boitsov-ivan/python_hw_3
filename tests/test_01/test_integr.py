import pytest


async def test_full_link_flow(client, db_session):
    # Создание ссылки
    response = client.post("/links/shorten", json={"original_URL": "https://flow-test.com"})
    assert response.status_code == 200
    short_url = response.json()["link"]["short_URL"]
    
    # Получение статистики
    stats_response = client.get(f"/links/{short_url}/stats")
    assert stats_response.status_code == 200
    assert stats_response.json()["clicks"] == 0
    
    # Переход по ссылке
    redirect_response = client.get(f"/links/{short_url}", follow_redirects=False)
    assert redirect_response.status_code == 302
    
    # Проверка обновленной статистики
    updated_stats = client.get(f"/links/{short_url}/stats")
    assert updated_stats.json()["clicks"] == 1




@pytest.mark.asyncio
async def test_full_link_flow(client, mocker):
    
    mocker.patch("app.users.dependencies.get_current_user", return_value=None)
    
 
    mocker.patch("app.links.dao.LinksDAO.find_one_or_none", return_value=None)
    mocker.patch("app.links.dao.LinksDAO.add", return_value=True)
    mocker.patch("app.links.dao.LinksDAO.update")
    
    
    create_resp = client.post("/links/shorten", json={"original_URL": "https://test.com"})
    short_url = create_resp.json()["link"]["short_URL"]
    
    
    stats_resp = client.get(f"/links/{short_url}/stats")
    assert stats_resp.status_code == 200
    
    
    redirect_resp = client.get(f"/links/{short_url}", follow_redirects=False)
    assert redirect_resp.status_code == 302
