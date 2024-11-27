from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from app.schemas.user import UserSchema


class LoginSchema(Schema):
    """Schema for user login request"""

    username = fields.String(required=True)
    password = fields.String(required=True)


class RegisterSchema(Schema):
    """Schema for user registration request"""

    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    confirm_password = fields.String(required=True)

    @validates("username")
    def validate_username(self, value):
        if len(value) < 3:
            raise ValidationError("Username must be at least 3 characters long")
        if len(value) > 80:
            raise ValidationError("Username must be less than 80 characters")

    @validates("password")
    def validate_password(self, value):
        errors = []
        special_chars = '!@#$%^&*(),.?":{}|<>'

        if len(value) < 8:
            errors.append("Password must be at least 8 characters long")

        if not any(char.isdigit() for char in value):
            errors.append("Password must contain at least one number")

        if not any(char.isupper() for char in value):
            errors.append("Password must contain at least one uppercase letter")

        if not any(char.islower() for char in value):
            errors.append("Password must contain at least one lowercase letter")

        if not any(char in special_chars for char in value):
            errors.append(
                f"Password must contain at \
            least one special character ({special_chars})"
            )

        if errors:
            raise ValidationError(errors)

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data.get("password") and data.get("confirm_password"):
            if data["password"] != data["confirm_password"]:
                raise ValidationError("Passwords must match", "confirm_password")


class PasswordResetRequestSchema(Schema):
    """Schema for password reset request"""

    email = fields.Email(required=True)


class PasswordResetSchema(Schema):
    """Schema for password reset"""

    token = fields.String(required=True)
    new_password = fields.String(required=True)
    confirm_password = fields.String(required=True)

    @validates("new_password")
    def validate_password(self, value):
        errors = []
        special_chars = '!@#$%^&*(),.?":{}|<>'

        if len(value) < 8:
            errors.append("Password must be at least 8 characters long")

        if not any(char.isdigit() for char in value):
            errors.append("Password must contain at least one number")

        if not any(char.isupper() for char in value):
            errors.append("Password must contain at least one uppercase letter")

        if not any(char.islower() for char in value):
            errors.append("Password must contain at least one lowercase letter")

        if not any(char in special_chars for char in value):
            errors.append(
                f"Password must contain at least \
            one special character ({special_chars})"
            )

        if errors:
            raise ValidationError(errors)

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data["new_password"] != data["confirm_password"]:
            raise ValidationError("Passwords must match", "confirm_password")


class PasswordChangeSchema(Schema):
    """Schema for password change"""

    current_password = fields.String(required=True)
    new_password = fields.String(required=True)
    confirm_password = fields.String(required=True)

    @validates("new_password")
    def validate_password(self, value):
        errors = []
        special_chars = '!@#$%^&*(),.?":{}|<>'

        if len(value) < 8:
            errors.append("Password must be at least 8 characters long")

        if not any(char.isdigit() for char in value):
            errors.append("Password must contain at least one number")

        if not any(char.isupper() for char in value):
            errors.append("Password must contain at least one uppercase letter")

        if not any(char.islower() for char in value):
            errors.append("Password must contain at least one lowercase letter")

        if not any(char in special_chars for char in value):
            errors.append(
                f"Password must contain at least \
              one special character ({special_chars})"
            )

        if errors:
            raise ValidationError(errors)

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data["new_password"] != data["confirm_password"]:
            raise ValidationError("Passwords must match", "confirm_password")


class TokenSchema(Schema):
    """Schema for JWT token response"""

    access_token = fields.String(required=True)
    token_type = fields.String(dump_default="bearer")
    expires_in = fields.Integer()


class AuthSuccessSchema(Schema):
    """Schema for successful authentication response"""

    message = fields.String()
    token = fields.Nested(TokenSchema)
    user = fields.Nested(UserSchema(exclude=("password",)))


class AuthErrorSchema(Schema):
    """Schema for authentication error response"""

    message = fields.String(required=True)
    errors = fields.Dict(keys=fields.String(), values=fields.List(fields.String()))
