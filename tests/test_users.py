def test_admin_can_list_users(client, create_user, get_token):
    create_user(role="admin", username="admin3")
    token = get_token("admin3")

    res = client.get("/users/list", headers={
        "Authorization": f"Bearer {token}"
    })

    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_viewer_cannot_list_users(client, create_user, get_token):
    create_user(role="viewer", username="viewer2")
    token = get_token("viewer2")

    res = client.get("/users/list", headers={
        "Authorization": f"Bearer {token}"
    })

    assert res.status_code == 403


def test_admin_cannot_delete_self(client, create_user, get_token):
    user = create_user(role="admin", username="admin4")
    token = get_token("admin4")

    res = client.delete(f"/users/{user['id']}", headers={
        "Authorization": f"Bearer {token}"
    })

    assert res.status_code == 400