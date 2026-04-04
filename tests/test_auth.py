def test_register_user(client):
    res = client.post("/auth/register", json={
        "name": "Test",
        "username": "testuser",
        "email": "test@test.com",
        "password": "password123"
    })

    assert res.status_code == 201
    assert res.json()["username"] == "testuser"


def test_login_success(client, create_user):
    create_user(username="user1")

    res = client.post("/auth/login", json={
        "username": "user1",
        "password": "password123"
    })

    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_invalid_password(client, create_user):
    create_user(username="user2")

    res = client.post("/auth/login", json={
        "username": "user2",
        "password": "wrong"
    })

    assert res.status_code == 401