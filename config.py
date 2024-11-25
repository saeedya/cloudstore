import os
from datetime import timedelta

class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql://dev_user:dev_pass@localhost/cloud_store_dev')
    DEBUG = True

class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql://test_user:test_pass@localhost/cloud_store_test')
    TESTING = True

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}