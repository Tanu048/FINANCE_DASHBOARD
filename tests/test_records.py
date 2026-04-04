def test_create_record_admin_only(client, create_user, get_token):
    create_user(role="admin", username="admin1")
    token = get_token("admin1")

    res = client.post(
        "/records/",
        json={
            "amount": 100,
            "type": "income",
            "category": "salary",
            "date": "2024-01-01",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 201


def test_create_record_forbidden_for_viewer(client, create_user, get_token):
    create_user(role="viewer", username="viewer1")
    token = get_token("viewer1")

    res = client.post(
        "/records/",
        json={
            "amount": 100,
            "type": "income",
            "category": "salary",
            "date": "2024-01-01",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 403


def test_get_summary(client, create_user, get_token):
    create_user(role="admin", username="admin2")
    token = get_token("admin2")

    # create records
    client.post(
        "/records/",
        json={
            "amount": 200,
            "type": "income",
            "category": "salary",
            "date": "2024-01-01",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    client.post(
        "/records/",
        json={
            "amount": 50,
            "type": "expense",
            "category": "food",
            "date": "2024-01-02",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    res = client.get("/records/summary", headers={"Authorization": f"Bearer {token}"})

    data = res.json()

    assert res.status_code == 200
    assert data["total_income"] == 200
    assert data["total_expenses"] == 50
    assert data["net_balance"] == 150
