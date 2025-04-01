import pytest
from pytest_mock import MockerFixture

@pytest.fixture
def mocker() -> MockerFixture:
    return MockerFixture(None)



from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)



from app.database import async_session_maker

@pytest.fixture
async def db_session():
    async with async_session_maker() as session:
        yield session
        await session.rollback()
