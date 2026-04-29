# tests/test_auth.py
# Fixtures (setup_db, client, db, lawyer_user) vêm do conftest.py automaticamente


def test_login_success(client, lawyer_user):
    response = client.post("/auth/login", json={"email": "advogado@test.com", "password": "senha123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, lawyer_user):
    response = client.post("/auth/login", json={"email": "advogado@test.com", "password": "errada"})
    assert response.status_code == 401


def test_login_user_not_found(client):
    response = client.post("/auth/login", json={"email": "naoexiste@test.com", "password": "123"})
    assert response.status_code == 401
