"""Tests for /register and /login endpoints."""


class TestRegister:
    def test_register_success(self, client):
        res = client.post("/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "secure123",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert "id" in data
        assert "hashed_password" not in data  # never expose this

    def test_register_duplicate_username(self, client, registered_user):
        res = client.post("/register", json={
            "username": registered_user["username"],
            "email": "other@example.com",
            "password": "password123",
        })
        assert res.status_code == 409
        assert "Username" in res.json()["detail"]

    def test_register_duplicate_email(self, client, registered_user):
        res = client.post("/register", json={
            "username": "differentuser",
            "email": registered_user["email"],
            "password": "password123",
        })
        assert res.status_code == 409
        assert "Email" in res.json()["detail"]

    def test_register_short_password(self, client):
        res = client.post("/register", json={
            "username": "user2",
            "email": "user2@example.com",
            "password": "123",  # < 6 chars
        })
        assert res.status_code == 422  # Pydantic validation

    def test_register_invalid_email(self, client):
        res = client.post("/register", json={
            "username": "user3",
            "email": "not-an-email",
            "password": "password123",
        })
        assert res.status_code == 422


class TestLogin:
    def test_login_success(self, client, registered_user):
        res = client.post("/login", json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, registered_user):
        res = client.post("/login", json={
            "username": registered_user["username"],
            "password": "wrongpassword",
        })
        assert res.status_code == 401

    def test_login_nonexistent_user(self, client):
        res = client.post("/login", json={
            "username": "ghost",
            "password": "password123",
        })
        assert res.status_code == 401
