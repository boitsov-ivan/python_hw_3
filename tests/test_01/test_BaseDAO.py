import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from app.dao.base import BaseDAO

Base = declarative_base()

class MockModel(Base):
    __tablename__ = 'mock_model'
    id = Column(Integer, primary_key=True)
    name = Column(String)

@pytest.fixture
def base_dao():
    class TestDAO(BaseDAO):
        model = MockModel
    return TestDAO

@pytest.mark.asyncio
async def test_find_all_success(base_dao):
    with patch('app.database.async_session_maker') as mock_session:
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            MockModel(id=1, name="Test1"),
            MockModel(id=2, name="Test2")
        ]
        mock_session.return_value.__aenter__.return_value.execute.return_value = mock_result
        
        result = await base_dao.find_all()
        assert len(result) == 2
        assert result[0].id == 1









@pytest.mark.asyncio
async def test_find_one_or_none_success():
    with patch('app.database.async_session_maker') as mock_session:
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = {"id": 1}
        mock_session.return_value.__aenter__.return_value.execute.return_value = mock_result
        
        result = await BaseDAO.find_one_or_none(id=1)
        assert result == {"id": 1}

@pytest.mark.asyncio
async def test_add_success():
    with patch('app.database.async_session_maker') as mock_session:
        mock_session.return_value.__aenter__.return_value.add.return_value = None
        mock_session.return_value.__aenter__.return_value.commit.return_value = None
        
        result = await BaseDAO.add(id=1, name="test")
        assert result is None




@pytest.mark.asyncio
async def test_update_success(base_dao):
    with patch('app.database.async_session_maker') as mock_session:
        mock_session.return_value.__aenter__.return_value.execute.return_value = None
        result = await base_dao.update({'id': 1}, name="Updated")
        assert result is None

@pytest.mark.asyncio
async def test_delete_success(base_dao):
    with patch('app.database.async_session_maker') as mock_session:
        mock_session.return_value.__aenter__.return_value.execute.return_value = None
        result = await base_dao.delete(id=1)
        assert result is None





