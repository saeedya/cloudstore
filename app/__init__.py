from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager  # type: ignore
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
migrate = Migrate()


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Health check endpoint
    @app.route("/health")
    def health_check():
        return jsonify({"status": "healthy", 
                        "database": db.engine.url.database})

    with app.app_context():
        db.create_all()

    return app
