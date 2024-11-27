import pytest
from marshmallow import ValidationError
from app.schemas.user import UserSchema
from app.models.user import User


def test_valid_user_serialization():
    """
    GIVEN a User instance
    WHEN serializing with UserSchema
    THEN check the serialization is correct
    """
    user = User(username="testuser", email="test@test.com")
    user.set_password("password123")

    schema = UserSchema()
    result = schema.dump(user)

    assert result["username"] == "testuser"
    assert result["email"] == "test@test.com"
    assert "password" not in result 
    assert "id" in result


def test_user_deserialization():
    """
    GIVEN valid user data
    WHEN deserializing with UserSchema
    THEN check instance is created correctly
    """
    user_data = {
        "username": "testuser",
        "email": "test@test.com",
        "password": "Password@123",
    }

    schema = UserSchema()
    user = schema.load(user_data)

    assert user.username == user_data["username"]
    assert user.email == user_data["email"]


def test_invalid_username():
    """
    GIVEN user data with invalid username
    WHEN validating with UserSchema
    THEN check validation error is raised
    """
    schema = UserSchema()

    with pytest.raises(ValidationError) as err:
        schema.load(
            {
                "username": "ab",  # too short
                "email": "test@test.com",
                "password": "password123",
            }
        )
    assert "username" in err.value.messages


def test_invalid_email():
    """
    GIVEN user data with invalid email
    WHEN validating with UserSchema
    THEN check validation error is raised
    """
    schema = UserSchema()

    with pytest.raises(ValidationError) as err:
        schema.load(
            {
                "username": "testuser",
                "email": "invalid-email",
                "password": "password123",
            }
        )
    assert "email" in err.value.messages


def test_invalid_password():
    """
    GIVEN user data with invalid password
    WHEN validating with UserSchema
    THEN check validation error is raised
    """
    schema = UserSchema()

    with pytest.raises(ValidationError) as err:
        schema.load(
            {
                "username": "testuser",
                "email": "test@test.com",
                "password": "short",  # too short
            }
        )
    assert "password" in err.value.messages
