from links.models import Link
import pytest

from datetime import datetime, timedelta


@pytest.fixture
def sample_link():
    return Link(
        id=1,
        original_URL="https://example.com",
        short_URL="abc123",
        clicks=0,
        expires_at=datetime.now() + timedelta(days=7),
        is_registered=False,
        id_user=None
    )

def test_link_initialization(sample_link):
    assert sample_link.id == 1
    assert sample_link.original_URL == "https://example.com"
    assert sample_link.short_URL == "abc123"
    assert sample_link.clicks == 0
    assert isinstance(sample_link.expires_at, datetime)
    assert sample_link.is_registered is False
    assert sample_link.id_user is None

def test_link_str_representation(sample_link):
    expected_str = "Link(id=1, original_URL='https://example.com', short_URL='abc123')"
    assert str(sample_link) == expected_str

def test_link_repr_representation(sample_link):
    """Тест repr представления объекта"""
    expected_repr = "Link(id=1, original_URL='https://example.com', short_URL='abc123')"
    assert repr(sample_link) == expected_repr

def test_link_to_dict_method(sample_link):
    """Тест метода to_dict()"""
    link_dict = sample_link.to_dict()
    
    assert isinstance(link_dict, dict)
    assert link_dict["id"] == 1
    assert link_dict["original_URL"] == "https://example.com"
    assert link_dict["short_URL"] == "abc123"
    assert link_dict["clicks"] == 0
    assert isinstance(link_dict["expires_at"], datetime)
    assert link_dict["is_registered"] is False
    assert link_dict["id_user"] is None
    assert "created_at" in link_dict
    assert "updated_at" in link_dict

def test_link_with_null_expires_at():
    link = Link(
        id=2,
        original_URL="https://no-expiry.com",
        short_URL="noexp",
        clicks=0,
        expires_at=None,
        is_registered=True,
        id_user=1
    )
    
    assert link.expires_at is None
    assert link.is_registered is True
    assert link.id_user == 1

def test_link_unique_constraints(sample_link, db_session):
    """Тест уникальности original_URL и short_URL"""
    db_session.add(sample_link)
    db_session.commit()
    
    with pytest.raises(Exception):
        duplicate = Link(
            original_URL=sample_link.original_URL,
            short_URL="different",
            clicks=0
        )
        db_session.add(duplicate)
        db_session.commit()
    
    with pytest.raises(Exception):
        duplicate = Link(
            original_URL="https://different.com",
            short_URL=sample_link.short_URL,
            clicks=0
        )
        db_session.add(duplicate)
        db_session.commit()

def test_link_default_values():
    """Тест значений по умолчанию"""
    link = Link(
        original_URL="https://default.com",
        short_URL="def123"
    )
    
    assert link.clicks == 0
    assert link.expires_at is None
    assert link.is_registered is False
    assert link.id_user is None




def test_link_model():
    link = Link(
        original_URL="https://test.com",
        short_URL="test123",
        clicks=0
    )
    assert str(link) == "Link(id=None)"


def test_link_schema():
    data = {
        "original_URL": "https://valid.com",
        "expires_at": datetime.now().isoformat()
    }
    schema = SLinkAddURLtime(**data)
    assert schema.original_URL == data["original_URL"]























