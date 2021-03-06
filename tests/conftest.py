import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
        }
    )

    with app.app_context():
        init_db()
        db = get_db()
        cursor = db.cursor()
        delete_test_sql = "DELETE FROM user where username = %s"
        user = ("test",)
        cursor.execute(delete_test_sql, user)
        with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
            cursor.execute(f.read().decode("utf-8"), multi=True)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
