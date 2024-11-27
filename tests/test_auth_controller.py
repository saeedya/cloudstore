import pytest, logging
from datetime import datetime, timedelta, timezone
from app.controllers.auth import AuthController
from app.models.user import User


@pytest.fixture
def auth_controller():
    return AuthController()


class TestAuthController:
    def test_successful_registration(self, auth_controller, db_session):
        """Test successful user registration"""
        data = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "TestPass123@",
            "confirm_password": "TestPass123@",
        }

        response, status_code = auth_controller.register(data)

        assert status_code == 201
        assert "token" in response
        assert "user" in response
        assert response["user"]["username"] == "testuser"
        assert response["user"]["email"] == "test@test.com"

        # Verify user was created in database
        user = User.query.filter_by(username="testuser").first()
        assert user is not None
        assert user.email == "test@test.com"

    def test_duplicate_username_registration(self, auth_controller, 
                                             db_session):
        """Test registration with existing username"""
        # Create existing user
        user = User(username="testuser", email="existing@test.com")
        user.set_password("TestPass123@")
        db_session.add(user)
        db_session.commit()

        # Try to register with same username
        data = {
            "username": "testuser",
            "email": "new@test.com",
            "password": "TestPass123@",
            "confirm_password": "TestPass123@",
        }

        response, status_code = auth_controller.register(data)

        assert status_code == 400
        assert "errors" in response
        assert "username" in response["errors"]

    def test_successful_login(self, auth_controller, db_session):
        """Test successful login"""
        # Create user
        user = User(username="testuser", email="test@test.com")
        user.set_password("TestPass123@")
        db_session.add(user)
        db_session.commit()

        # Login
        data = {"username": "testuser", "password": "TestPass123@"}

        response, status_code = auth_controller.login(data)

        assert status_code == 200
        assert "token" in response
        assert "user" in response
        assert response["user"]["username"] == "testuser"

    def test_invalid_login(self, auth_controller, db_session):
        """Test login with invalid credentials"""
        # Create user
        user = User(username="testuser", email="test@test.com")
        user.set_password("TestPass123@")
        db_session.add(user)
        db_session.commit()

        # Try wrong password
        data = {"username": "testuser", "password": "WrongPass123@"}

        response, status_code = auth_controller.login(data)

        assert status_code == 401
        assert "errors" in response

    def test_inactive_user_login(self, auth_controller, db_session):
        """Test login with inactive user"""
        # Create inactive user
        user = User(username="testuser", email="test@test.com", 
                    is_active=False)
        user.set_password("TestPass123@")
        db_session.add(user)
        db_session.commit()

        data = {"username": "testuser", "password": "TestPass123@"}

        response, status_code = auth_controller.login(data)

        assert status_code == 401
        assert "Account is disabled" in str(response["errors"]["_error"])

    def test_request_password_reset(self, auth_controller, db_session):
        """Test password reset request"""
        # Create user
        user = User(username="testuser", email="test@test.com")
        user.set_password("TestPass123@")
        db_session.add(user)
        db_session.commit()

        response, status_code = \
                    auth_controller.request_password_reset("test@test.com")
        assert status_code == 200
        assert "message" in response

        # Verify reset token was set
        user = User.query.filter_by(email="test@test.com").first()
        assert user.reset_token is not None
        assert user.reset_token_expires is not None

    def test_reset_password(self, auth_controller, db_session):
        """Test password reset"""
        try:
            # Create user with reset token
            expiry = datetime.now(timezone.utc) + timedelta(hours=1)
            logging.info(f"Setting token expiry to: {expiry} (UTC)")

            user = User(
                username="testuser",
                email="test@test.com",
                reset_token="valid-token",
                reset_token_expires=expiry,
            )
            user.set_password("TestPass123@")
            db_session.add(user)
            db_session.commit()

            # Verify user was created properly
            created_user = User.query.filter_by(username="testuser").first()
            assert created_user is not None, "User was not created"
            assert created_user.reset_token == "valid-token", \
                            "Reset token not set"
            assert (
                created_user.reset_token_expires is not None
            ), "Reset token expiry not set"

            # Log timezone information
            logging.info(f"Stored token expiry: \
                          {created_user.reset_token_expires}")
            logging.info(
                f"Token expiry timezone info: \
                    {created_user.reset_token_expires.tzinfo}"
            )

            # Attempt password reset
            response, status_code = auth_controller.reset_password(
                "valid-token", "NewPass123@"
            )

            if status_code != 200:
                logging.error(f"Reset password failed: {response}")

            assert (
                status_code == 200
            ), f"Expected status 200, got {status_code}. Response: {response}"

            # Verify changes
            updated_user = User.query.filter_by(username="testuser").first()
            assert updated_user.check_password(
                "NewPass123@"
            ), "Password was not updated"
            assert updated_user.reset_token is None, \
                "Reset token was not cleared"
            assert (
                updated_user.reset_token_expires is None
            ), "Reset token expiry was not cleared"

        except Exception as e:
            logging.error(f"Test failed with error: {str(e)}")
            raise

    @pytest.fixture(autouse=True)
    def setup_logging(self):
        logging.basicConfig(level=logging.DEBUG)

    def test_change_password(self, auth_controller, db_session):
        """Test password change"""
        # Create user
        user = User(username="testuser", email="test@test.com")
        user.set_password("TestPass123@")
        db_session.add(user)
        db_session.commit()

        response, status_code = auth_controller.change_password(
            user.id, "TestPass123@", "NewPass123@"
        )
        assert status_code == 200
        assert "message" in response

        # Verify password was changed
        user = User.query.filter_by(email="test@test.com").first()
        assert user.check_password("NewPass123@")

    def test_verify_email(self, auth_controller, db_session):
        """Test email verification"""
        # Create user
        user = User(
            username="testuser",
            email="test@test.com",
            email_verification_token="verify-token",
            email_verified=False,
        )
        user.set_password("TestPass123@")
        db_session.add(user)
        db_session.commit()

        response, status_code = auth_controller.verify_email("verify-token")
        assert status_code == 200
        assert "message" in response

        # Verify email was verified
        user = User.query.filter_by(email="test@test.com").first()
        assert user.email_verified is True
        assert user.email_verification_token is None

    def test_update_profile(self, auth_controller, db_session):
        """Test profile update"""
        # Create user
        user = User(username="testuser", email="test@test.com")
        user.set_password("TestPass123@")
        db_session.add(user)
        db_session.commit()

        update_data = {"username": "newusername", 
                       "email": "newemail@test.com"}

        response, status_code = \
                    auth_controller.update_profile(user.id, update_data)
        assert status_code == 200
        assert "message" in response
        assert response["user"]["username"] == "newusername"
        assert response["user"]["email"] == "newemail@test.com"
