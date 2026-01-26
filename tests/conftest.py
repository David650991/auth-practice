import pytest

from app import create_app


@pytest.fixture(scope="session")
def app():
    app = create_app("config.development.DevelopmentConfig")
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()
