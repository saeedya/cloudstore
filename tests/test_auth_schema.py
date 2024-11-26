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
        schema = LoginSchema()
        data = {
            'username': 'testuser',
            'password': 'TestPass123'
        }
        result = schema.load(data)
        assert result == data

    def test_invalid_login_missing_fields(self):
        schema = LoginSchema()
        with pytest.raises(ValidationError) as err:
            schema.load({})
        assert 'username' in err.value.messages
        assert 'password' in err.value.messages

class TestRegisterSchema:
    def test_valid_registration(self):
        schema = RegisterSchema()
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123@',
            'confirm_password': 'TestPass123@'
        }
        result = schema.load(data)
        assert result == data

    def test_invalid_password(self):
        schema = RegisterSchema()
        test_cases = [
            ('short12', ['Password must be at least 8 characters long']),
            ('nouppercase123!', ['Password must contain at least one uppercase letter']),
            ('NOLOWERCASE123!', ['Password must contain at least one lowercase letter']),
            ('NoSpecialChar123', ['Password must contain at least one special character']),
            ('NoNumbers@Abc', ['Password must contain at least one number']),
        ]
        
        for password, expected_errors in test_cases:
            data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': password,
                'confirm_password': password
            }
            with pytest.raises(ValidationError) as err:
                schema.load(data)
            assert 'password' in err.value.messages
            for error in expected_errors:
                assert any(error in msg for msg in err.value.messages['password'])

    def test_password_mismatch(self):
        schema = RegisterSchema()
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123@',
            'confirm_password': 'DifferentPass123@'
        }
        with pytest.raises(ValidationError) as err:
            schema.load(data)
        assert 'confirm_password' in err.value.messages

    def test_missing_fields(self):
        schema = RegisterSchema()
        with pytest.raises(ValidationError) as err:
            schema.load({})
        assert 'username' in err.value.messages
        assert 'email' in err.value.messages
        assert 'password' in err.value.messages
        assert 'confirm_password' in err.value.messages

    def test_invalid_password(self):
        schema = RegisterSchema()
        test_cases = [
            ('short12', 'Too short'),
            ('nouppercase123!', 'No uppercase'),
            ('NOLOWERCASE123!', 'No lowercase'),
            ('NoSpecialChar123', 'No special character'),
            ('NoNumbers@Abc', 'No numbers'),
            ('Test@12', 'Too short with special char'),
        ]
        
        for password, case in test_cases:
            data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': password,
                'confirm_password': password
            }
            with pytest.raises(ValidationError) as err:
                schema.load(data)
                pytest.fail(f"Password validation should fail for case: {case}")
            assert 'password' in err.value.messages

    def test_valid_registration(self):
        schema = RegisterSchema()
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123@',  # Updated with special character
            'confirm_password': 'TestPass123@'
        }
        result = schema.load(data)
        assert result == data
    def test_password_mismatch(self):
        schema = RegisterSchema()
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test@Pass123',
            'confirm_password': 'Different@Pass123'
        }
        with pytest.raises(ValidationError) as err:
            schema.load(data)
        assert 'confirm_password' in err.value.messages

class TestResponseSchemas:
    def test_token_schema(self):
        schema = TokenSchema()
        data = {
            'access_token': 'eyJ0eXAi...',
            'token_type': 'bearer',
            'expires_in': 3600
        }
        result = schema.dump(data)
        assert result == data

    def test_auth_success_schema(self):
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
                'email': 'test@example.com'
            }
        }
        result = schema.dump(data)
        assert 'message' in result
        assert 'token' in result
        assert 'user' in result
        assert 'password' not in result['user']

    def test_auth_error_schema(self):
        schema = AuthErrorSchema()
        data = {
            'message': 'Validation failed',
            'errors': {
                'username': ['Username already exists'],
                'email': ['Invalid email format']
            }
        }
        result = schema.dump(data)
        assert result == data