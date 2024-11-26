import pytest
from app.models.user import User


def test_create_user(db_session):
    """
    GIVEN a User model
    WHEN creating a new user
    THEN check fields are defined correctly
    """
    user = User(username="testuser", email="test@test.com")
    user.set_password("testpass123")
    db_session.add(user)
    db_session.commit()

    # Verify UUID was generated
    assert len(user.id) == 32  # UUID hex length

    saved_user = db_session.query(User).filter_by(username="testuser").first()
    assert saved_user.username == "testuser"
    assert saved_user.email == "test@test.com"
    assert saved_user.check_password("testpass123")
    assert not saved_user.check_password("wrongpass")
    assert saved_user.is_active == True


def test_uuid_uniqueness(db_session):
    """
    GIVEN multiple users
    WHEN creating users
    THEN check each gets unique UUID
    """
    user1 = User(username="user1", email="test1@test.com")
    user2 = User(username="user2", email="test2@test.com")
    user1.set_password("testpass123")
    user2.set_password("testpass123")

    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()

    assert user1.id != user2.id
    assert len(user1.id) == 32
    assert len(user2.id) == 32


def test_unique_username(db_session):
    """
    GIVEN an existing user
    WHEN creating another user with same username
    THEN check it raises an error
    """
    user1 = User(username="testuser", email="test1@test.com")
    user1.set_password("testpass123")
    db_session.add(user1)
    db_session.commit()

    with pytest.raises(Exception):
        user2 = User(username="testuser", email="test2@test.com")
        user2.set_password("testpass123")
        db_session.add(user2)
        db_session.commit()


def test_unique_email(db_session):
    """
    GIVEN an existing user
    WHEN creating another user with same email
    THEN check it raises an error
    """
    user1 = User(username="user1", email="test@test.com")
    user1.set_password("testpass123")
    db_session.add(user1)
    db_session.commit()

    with pytest.raises(Exception):
        user2 = User(username="user2", email="test@test.com")
        user2.set_password("testpass123")
        db_session.add(user2)
        db_session.commit()
