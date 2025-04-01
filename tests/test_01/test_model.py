# tests/test_models.py
from app.links.models import Link
from app.users.models import User

def test_link_model():
    link = Link(
        original_URL="https://example.com",
        short_URL="abc123",
        clicks=0
    )
    assert "abc123" in str(link)

def test_user_model():
    user = User(
        phone_number="+1234567890",
        email="test@example.com",
        password="hash"
    )
    assert "User" in repr(user)
