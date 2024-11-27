from datetime import timedelta, datetime, timezone
import logging
import secrets
from flask_jwt_extended import create_access_token  # type: ignore
from app import db
from app.models.user import User
from app.schemas.auth import (
    LoginSchema,
    RegisterSchema,
    AuthSuccessSchema,
    AuthErrorSchema,
    PasswordResetSchema,
    PasswordChangeSchema,
    PasswordResetRequestSchema,
)


class AuthController:
    def __init__(self):
        self.login_schema = LoginSchema()
        self.register_schema = RegisterSchema()
        self.success_schema = AuthSuccessSchema()
        self.error_schema = AuthErrorSchema()
        self.password_reset_schema = PasswordResetSchema()
        self.password_change_schema = PasswordChangeSchema()
        self.password_reset_request_schema = PasswordResetRequestSchema()

    def register(self, data):
        """
        Handle User Registration Process:
        1. Validate input data
        2. Check for existing users
        3. Create new user
        4. Generate JWT token
        5. Return response
        """
        try:
            # Check if user already exists
            if User.query.filter_by(username=data["username"]).first():
                return (
                    self.error_schema.dump(
                        {
                            "message": "Registration failed",
                            "errors": {"username": ["Username already exists"]},
                        }
                    ),
                    400,
                )

            if User.query.filter_by(email=data["email"]).first():
                return (
                    self.error_schema.dump(
                        {
                            "message": "Registration failed",
                            "errors": {"email": ["Email already exists"]},
                        }
                    ),
                    400,
                )

            # Create new user
            user = User(username=data["username"], email=data["email"])
            user.set_password(data["password"])

            # Save to database
            db.session.add(user)
            db.session.commit()

            # Create access token
            access_token = create_access_token(
                identity=user.id, expires_delta=timedelta(days=1)
            )

            # Return success response
            return (
                self.success_schema.dump(
                    {
                        "message": "Registration successful",
                        "token": {"access_token": access_token, "token_type": "bearer"},
                        "user": user,
                    }
                ),
                201,
            )

        except Exception as e:
            db.session.rollback()
            return (
                self.error_schema.dump(
                    {"message": "Registration failed", "errors": {"_error": [str(e)]}}
                ),
                500,
            )

    def login(self, data):
        """
        Authenticate a user
        """
        try:
            # Find user
            user = User.query.filter_by(username=data["username"]).first()

            # Verify password
            if not user or not user.check_password(data["password"]):
                return (
                    self.error_schema.dump(
                        {
                            "message": "Login failed",
                            "errors": {"_error": ["Invalid username or password"]},
                        }
                    ),
                    401,
                )

            # Check if user is active
            if not user.is_active:
                return (
                    self.error_schema.dump(
                        {
                            "message": "Login failed",
                            "errors": {"_error": ["Account is disabled"]},
                        }
                    ),
                    401,
                )

            # Create access token
            access_token = create_access_token(
                identity=user.id, expires_delta=timedelta(days=1)
            )

            # Return success response
            return (
                self.success_schema.dump(
                    {
                        "message": "Login successful",
                        "token": {"access_token": access_token, "token_type": "bearer"},
                        "user": user,
                    }
                ),
                200,
            )

        except Exception as e:
            return (
                self.error_schema.dump(
                    {"message": "Login failed", "errors": {"_error": [str(e)]}}
                ),
                500,
            )

    def request_password_reset(self, email):
        """
        Generate password reset token and send reset email
        """
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                return (
                    self.error_schema.dump(
                        {
                            "message": "If email exists, \
                    reset instructions will be sent"
                        }
                    ),
                    200,
                )  # Return 200 to prevent email enumeration

            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            user.reset_token = reset_token
            user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)

            db.session.commit()

            # In real application, send email here
            # self.send_reset_email(user.email, reset_token)

            return (
                self.success_schema.dump(
                    {"message": "Password reset instructions sent"}
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            return (
                self.error_schema.dump(
                    {
                        "message": "Failed to process reset request",
                        "errors": {"_error": [str(e)]},
                    }
                ),
                500,
            )

    def reset_password(self, token, new_password):
        """Reset password using reset token"""
        try:
            # Debug logging
            logging.debug(f"Attempting to reset password with token: {token}")

            user = User.query.filter_by(reset_token=token).first()
            if not user:
                logging.debug("No user found with this token")
                return {
                    "message": "Invalid or expired reset token",
                    "errors": {"token": ["Invalid or expired token"]},
                }, 400

            # Debug datetime information
            current_time = datetime.now(timezone.utc)
            logging.debug(f"Current time (UTC): {current_time}")
            logging.debug(f"Token expires at: {user.reset_token_expires}")
            logging.debug(
                f"Token expires timezone info: \
                {user.reset_token_expires.tzinfo}"
            )

            if not user.is_valid_reset_token():
                logging.debug("Token validation failed")
                return {
                    "message": "Invalid or expired reset token",
                    "errors": {"token": ["Token has expired"]},
                }, 400

            # Update password
            user.set_password(new_password)
            user.reset_token = None
            user.reset_token_expires = None

            db.session.commit()
            logging.debug("Password successfully reset")

            return {"message": "Password successfully reset"}, 200

        except Exception as e:
            logging.error(f"Error in reset_password: {str(e)}")
            db.session.rollback()
            return {
                "message": "Failed to reset password",
                "errors": {"_error": [str(e)]},
            }, 500

    def is_valid_reset_token(self, user):
        """Helper method to validate reset token"""
        if not user.reset_token or not user.reset_token_expires:
            return False
        return datetime.now(timezone.utc) < user.reset_token_expires

    def change_password(self, user_id, current_password, new_password):
        """
        Change password for authenticated user
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                return self.error_schema.dump({"message": "User not found"}), 404

            if not user.check_password(current_password):
                return (
                    self.error_schema.dump(
                        {
                            "message": "Current password is incorrect",
                            "errors": {"current_password": ["Invalid password"]},
                        }
                    ),
                    400,
                )

            user.set_password(new_password)
            db.session.commit()

            return (
                self.success_schema.dump({"message": "Password successfully changed"}),
                200,
            )

        except Exception as e:
            db.session.rollback()
            return (
                self.error_schema.dump(
                    {
                        "message": "Failed to change password",
                        "errors": {"_error": [str(e)]},
                    }
                ),
                500,
            )

    def verify_email(self, token):
        """
        Verify user's email address
        """
        try:
            user = User.query.filter_by(email_verification_token=token).first()

            if not user:
                return (
                    self.error_schema.dump({"message": "Invalid verification token"}),
                    400,
                )

            user.email_verified = True
            user.email_verification_token = None

            db.session.commit()

            return (
                self.success_schema.dump({"message": "Email successfully verified"}),
                200,
            )

        except Exception as e:
            db.session.rollback()
            return (
                self.error_schema.dump(
                    {
                        "message": "Failed to verify email",
                        "errors": {"_error": [str(e)]},
                    }
                ),
                500,
            )

    def update_profile(self, user_id, data):
        """
        Update user profile information
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                return self.error_schema.dump({"message": "User not found"}), 404

            # Update allowed fields
            for field in ["username", "email"]:
                if field in data:
                    setattr(user, field, data[field])

            db.session.commit()

            return (
                self.success_schema.dump(
                    {"message": "Profile updated successfully", "user": user}
                ),
                200,
            )

        except Exception as e:
            db.session.rollback()
            return (
                self.error_schema.dump(
                    {
                        "message": "Failed to update profile",
                        "errors": {"_error": [str(e)]},
                    }
                ),
                500,
            )
