import pytest
from marshmallow import ValidationError
from app.schemas.auth import (
    LoginSchema, 
    RegisterSchema,
    TokenSchema,
    AuthSuccessSchema,
    AuthErrorSchema
)

class TestLoginSchema:
    def test_valid_login(self):
        """Test valid login data"""
        schema = LoginSchema()
        data = {
            'username': 'testuser',
            'password': 'TestPass123@'
        }
        result = schema.load(data)
        assert result == data

    def test_missing_fields(self):
        """Test login with missing fields"""
        schema = LoginSchema()
        with pytest.raises(ValidationError) as err:
            schema.load({})
        assert 'username' in err.value.messages
        assert 'password' in err.value.messages

class TestRegisterSchema:
    def test_valid_registration(self):
        """Test valid registration data"""
        schema = RegisterSchema()
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123@',
            'confirm_password': 'TestPass123@'
        }
        result = schema.load(data)
        assert result == data

    def test_password_validation(self):
        """Test password requirements"""
        schema = RegisterSchema()
        test_cases = [
            ('short1@', 'at least 8 characters'),  # Match exact error message
            ('nouppercasechar1@', 'uppercase letter'),
            ('NOLOWERCASECHAR1@', 'lowercase letter'),
            ('NoSpecialChar123', 'special character'),
            ('NoNumber@Abcd', 'must contain at least one number')
        ]

        for password, expected_error in test_cases:
            data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': password,
                'confirm_password': password
            }
            with pytest.raises(ValidationError) as err:
                schema.load(data)

            # Verify the correct error was raised
            error_messages = err.value.messages.get('password', [])
            error_found = any(expected_error in str(msg).lower() for msg in error_messages)
            assert error_found, (
                f"Password '{password}' should have failed with message containing '{expected_error}'. "
                f"Got messages: {error_messages}"
            )

    def test_invalid_username(self):
        """Test username validation"""
        schema = RegisterSchema()
        with pytest.raises(ValidationError) as err:
            schema.load({
                'username': 'te',
                'email': 'test@example.com',
                'password': 'TestPass123@',
                'confirm_password': 'TestPass123@'
            })
        assert 'username' in err.value.messages

    def test_invalid_email(self):
        """Test email validation"""
        schema = RegisterSchema()
        with pytest.raises(ValidationError) as err:
            schema.load({
                'username': 'testuser',
                'email': 'invalid-email',
                'password': 'TestPass123@',
                'confirm_password': 'TestPass123@'
            })
        assert 'email' in err.value.messages

    def test_password_mismatch(self):
        """Test password confirmation"""
        schema = RegisterSchema()
        with pytest.raises(ValidationError) as err:
            schema.load({
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'TestPass123@',
                'confirm_password': 'DifferentPass123@'
            })
        assert 'confirm_password' in err.value.messages

class TestResponseSchemas:
    def test_token_schema(self):
        """Test token response format"""
        schema = TokenSchema()
        data = {
            'access_token': 'eyJ0eXAi...',
            'token_type': 'bearer',
            'expires_in': 3600
        }
        result = schema.dump(data)
        assert result == data

    def test_auth_success_response(self):
        """Test successful authentication response"""
        schema = AuthSuccessSchema()
        data = {
            'message': 'Login successful',
            'token': {
                'access_token': 'eyJ0eXAi...',
                'token_type': 'bearer',
                'expires_in': 3600
            },
            'user': {
                'id': '123',
                'username': 'testuser',
                'email': 'test@example.com',
                'role': 'user'
            }
        }
        result = schema.dump(data)
        assert 'message' in result
        assert 'token' in result
        assert 'user' in result
        assert 'password' not in result['user']

    def test_auth_error_response(self):
        """Test authentication error response"""
        schema = AuthErrorSchema()
        data = {
            'message': 'Authentication failed',
            'errors': {
                'username': ['User not found'],
                'password': ['Invalid password']
            }
        }
        result = schema.dump(data)
        assert result == data