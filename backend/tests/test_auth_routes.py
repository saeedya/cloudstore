import json
import pytest
from app.models.user import User

@pytest.fixture
def test_user(db_session):
    user = User(username='testuser', email='test@test.com')
    user.set_password('TestPass123@')
    db_session.add(user)
    db_session.commit()
    return user

class TestAuthRoutes:
    def test_register(self, client):
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'TestPass123@',
            'confirm_password': 'TestPass123@'
        }
        response = client.post(
            '/api/v1/auth/register',
            json=data
        )
        assert response.status_code == 201
        assert 'token' in response.json
        assert response.json['user']['username'] == 'newuser'

    def test_login(self, client, test_user):
        data = {
            'username': 'testuser',
            'password': 'TestPass123@'
        }
        response = client.post(
            '/api/v1/auth/login',
            json=data
        )
        assert response.status_code == 200
        assert 'token' in response.json

    def test_reset_password(self, client, test_user):
        # First request password reset
        response = client.post(
            '/api/v1/auth/reset-password',
            json={'token': 'valid-token', 'new_password': 'NewPass123@'}
        )
        assert response.status_code in [200, 400]

    def test_change_password(self, client, test_user):
        # Login first to get token
        login_response = client.post(
            '/api/v1/auth/login',
            json={'username': 'testuser', 'password': 'TestPass123@'}
        )
        token = login_response.json['token']['access_token']

        # Change password
        response = client.post(
            '/api/v1/auth/change-password',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'current_password': 'TestPass123@',
                'new_password': 'NewPass123@',
                'confirm_password': 'NewPass123@'
            }
        )
        assert response.status_code == 200

    def test_get_profile(self, client, test_user):
        # Login first
        login_response = client.post(
            '/api/v1/auth/login',
            json={'username': 'testuser', 'password': 'TestPass123@'}
        )
        token = login_response.json['token']['access_token']

        # Get profile
        response = client.get(
            '/api/v1/auth/profile',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        assert response.json['username'] == 'testuser'

    def test_update_profile(self, client, test_user):
        # Login first
        login_response = client.post(
            '/api/v1/auth/login',
            json={'username': 'testuser', 'password': 'TestPass123@'}
        )
        token = login_response.json['token']['access_token']

        # Update profile
        response = client.put(
            '/api/v1/auth/profile',
            headers={'Authorization': f'Bearer {token}'},
            json={'username': 'updateduser'}
        )
        assert response.status_code == 200
        assert response.json['user']['username'] == 'updateduser'