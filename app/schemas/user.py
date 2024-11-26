from marshmallow import fields, validates, ValidationError
from app import ma
from app.models.user import User

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True

    id = ma.String(dump_only=True)
    username = ma.String(required=True)
    email = ma.Email(required=True)
    password = ma.String(required=True, load_only=True)
    created_at = ma.DateTime(dump_only=True)
    is_active = ma.Boolean(dump_only=True)
    role = ma.String(dump_only=True)

    @validates('username')
    def validate_username(self, value):
        if len(value) < 3:
            raise ValidationError('Username must be at least 3 characters long')
        if len(value) > 80:
            raise ValidationError('Username must be less than 80 characters')

    @validates('password')
    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError('Password must be at least 8 characters long')
