# app/models/user.py
from datetime import datetime, timezone
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    __tablename__ = "users"

    # UUID as String for MySQL compatibility
    id = db.Column(db.String(32), 
                   primary_key=True, default=lambda: uuid4().hex)
    username = db.Column(
        db.String(80, collation="utf8mb4_unicode_ci"), 
        unique=True, nullable=False
    )
    email = db.Column(
        db.String(120, collation="utf8mb4_unicode_ci"), 
        unique=True, nullable=False
    )
    password_hash = db.Column(
        db.String(255, collation="utf8mb4_unicode_ci"), nullable=False
    )
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20, collation="utf8mb4_unicode_ci"), 
                     default="user")

    # Reset password fields
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expires = db.Column(db.DateTime)

    # Email verification fields
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(100), unique=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_valid_reset_token(self):
        if not self.reset_token or not self.reset_token_expires:
            return False

        # Ensure comparison uses timezone-aware datetime
        current_time = datetime.now(timezone.utc)

        # If reset_token_expires is naive, make it aware
        expires_at = self.reset_token_expires
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        return current_time < expires_at

    def __repr__(self):
        return f"<User {self.username}>"
