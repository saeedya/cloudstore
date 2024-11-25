from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager # type: ignore
from config import config

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    return app