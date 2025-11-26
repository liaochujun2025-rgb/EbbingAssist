from http import HTTPStatus

from backend.extensions import db


def test_register_and_login_and_refresh_and_logout(client):
    # register
    resp = client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "Secret123!"},
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json["data"]
    user_id = data["user_id"]
    tokens = data["tokens"]
    assert tokens["access"]
    assert tokens["refresh"]

    # login with account alias (email)
    login_resp = client.post(
        "/api/auth/login",
        json={"account": "user@example.com", "password": "Secret123!"},
    )
    assert login_resp.status_code == HTTPStatus.OK
    login_tokens = login_resp.json["data"]["tokens"]
    assert login_tokens["access"]
    assert login_tokens["refresh"]

    # refresh
    refresh_resp = client.post(
        "/api/auth/refresh",
        headers={"Authorization": f"Bearer {login_tokens['refresh']}"},
    )
    assert refresh_resp.status_code == HTTPStatus.OK
    assert refresh_resp.json["data"]["access"]

    # logout invalidates token
    logout_resp = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {login_tokens['refresh']}"},
    )
    assert logout_resp.status_code == HTTPStatus.OK

    # refresh after logout should still fail when token revoked
    post_logout = client.post(
        "/api/auth/refresh",
        headers={"Authorization": f"Bearer {login_tokens['refresh']}"},
    )
    assert post_logout.status_code == HTTPStatus.UNAUTHORIZED
    assert post_logout.json["code"] == 2003
