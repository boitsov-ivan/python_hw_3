# tests/test_main.py
from app.main import app



def test_main_app_config():
    assert app.title == "FastAPI"
