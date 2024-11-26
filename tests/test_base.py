import pytest
from app import create_app, db


def test_app_creates():
    """
    GIVEN our Flask application
    WHEN we create a test instance
    THEN check the app is created with test config
    """
    app = create_app("testing")
    assert app is not None
    assert app.config["TESTING"] is True


def test_app_database():
    """
    GIVEN our Flask application
    WHEN we initialize database
    THEN check the database is accessible
    """
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        assert db is not None
        db.drop_all()


def test_health_check(client):
    """
    GIVEN our Flask application
    WHEN we request '/'
    THEN we should get a 200 response
    """
    response = client.get("/health")
    assert response.status_code == 200
