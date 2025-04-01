# tests/test_schemas.py
from app.links.schemas import SLinkAddURLtime
from datetime import datetime

def test_link_schema_validation():
    data = {
        "original_URL": "https://valid.com",
        "alias": None,
        "expires_at": datetime.now().isoformat()
    }
    schema = SLinkAddURLtime(**data)
    assert schema.original_URL == data["original_URL"]
