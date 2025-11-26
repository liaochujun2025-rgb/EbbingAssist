from http import HTTPStatus


def test_profile_requires_auth(client):
    resp = client.get("/api/user/profile")
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_profile_success(client):
    # register and login to get token
    reg = client.post("/api/auth/register", json={"email": "p1@example.com", "password": "Secret123!"})
    token = reg.json["data"]["tokens"]["access"]
    resp = client.get("/api/user/profile", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == HTTPStatus.OK
    data = resp.json["data"]
    assert data["email"] == "p1@example.com"
    assert data["roles"] == ["user"]
