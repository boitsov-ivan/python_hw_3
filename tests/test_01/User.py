from users.models import User
import pytest



import pytest
from sqlalchemy.exc import IntegrityError
from app.models.user import User

@pytest.fixture
def sample_user():
    """Фикстура для создания тестового пользователя"""
    return User(
        phone_number="+1234567890",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password="securepassword123",
        is_admin=False
    )

def test_user_creation(sample_user):
    """Тест базового создания пользователя"""
    assert sample_user.phone_number == "+1234567890"
    assert sample_user.first_name == "John"
    assert sample_user.last_name == "Doe"
    assert sample_user.email == "john.doe@example.com"
    assert sample_user.password == "securepassword123"
    assert sample_user.is_admin is False
    assert sample_user.id is None  

def test_user_repr(sample_user):
    """Тест строкового представления"""
    assert repr(sample_user) == "User(id=None)"  
    assert repr(sample_user) == "User(id=1)"  
def test_user_unique_constraints(db_session, sample_user):
    """Тест уникальности phone_number и email"""
    db_session.add(sample_user)
    db_session.commit()
    
    with pytest.raises(IntegrityError):
        duplicate_phone = User(
            phone_number="+1234567890",  
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            password="anotherpassword"
        )
        db_session.add(duplicate_phone)
        db_session.commit()
    db_session.rollback()
    
    
    with pytest.raises(IntegrityError):
        duplicate_email = User(
            phone_number="+9876543210",
            first_name="Jane",
            last_name="Doe",
            email="john.doe@example.com",  
            password="anotherpassword"
        )
        db_session.add(duplicate_email)
        db_session.commit()
    db_session.rollback()

def test_user_is_admin_default(db_session):
    """Тест значения по умолчанию для is_admin"""
    user = User(
        phone_number="+1111111111",
        first_name="Default",
        last_name="User",
        email="default@example.com",
        password="password"
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.is_admin is False

def test_user_null_constraints(db_session):
    """Тест обязательных полей"""
    with pytest.raises(IntegrityError):
        user = User()  # Все обязательные поля отсутствуют
        db_session.add(user)
        db_session.commit()
    db_session.rollback()
    
    # Тест каждого обязательного поля по отдельности
    required_fields = ['phone_number', 'first_name', 'last_name', 'email', 'password']
    for field in required_fields:
        with pytest.raises(IntegrityError):
            user_data = {
                "phone_number": "+1234567890",
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com",
                "password": "password"
            }
            user_data.pop(field)
            user = User(**user_data)
            db_session.add(user)
            db_session.commit()
        db_session.rollback()

def test_user_admin_flag(db_session):
    """Тест установки флага администратора"""
    admin_user = User(
        phone_number="+9999999999",
        first_name="Admin",
        last_name="User",
        email="admin@example.com",
        password="adminpass",
        is_admin=True
    )
    db_session.add(admin_user)
    db_session.commit()
    
    assert admin_user.is_admin is True
    fetched_user = db_session.get(User, admin_user.id)
    assert fetched_user.is_admin is True

def test_user_update(db_session, sample_user):
    """Тест обновления данных пользователя"""
    db_session.add(sample_user)
    db_session.commit()
    
    # Обновляем данные
    sample_user.first_name = "Jonathan"
    sample_user.last_name = "Smith"
    db_session.commit()
    
    updated_user = db_session.get(User, sample_user.id)
    assert updated_user.first_name == "Jonathan"
    assert updated_user.last_name == "Smith"
    assert updated_user.phone_number == "+1234567890"  # Неизмененное поле

def test_user_delete(db_session, sample_user):
    """Тест удаления пользователя"""
    db_session.add(sample_user)
    db_session.commit()
    
    user_id = sample_user.id
    db_session.delete(sample_user)
    db_session.commit()
    
    deleted_user = db_session.get(User, user_id)
    assert deleted_user is None