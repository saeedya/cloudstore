# app/models/user.py
from datetime import datetime, timezone
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    __tablename__ = 'users'

    # UUID as String for MySQL compatibility
    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid4().hex)
    username = db.Column(db.String(80, collation='utf8mb4_unicode_ci'), unique=True, nullable=False)
    email = db.Column(db.String(120, collation='utf8mb4_unicode_ci'), unique=True, nullable=False)
    password_hash = db.Column(db.String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20, collation='utf8mb4_unicode_ci'), default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'