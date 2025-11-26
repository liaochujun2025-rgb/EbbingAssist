from http import HTTPStatus

import pytest


@pytest.fixture
def auth_headers(client):
    resp = client.post("/api/auth/register", json={"email": "log@example.com", "password": "Secret123!"})
    token = resp.json["data"]["tokens"]["access"]
    return {"Authorization": f"Bearer {token}"}


def _create_entry(client, headers):
    topic = client.post("/api/knowledge/topics", headers=headers, json={"name": "Topic1"}).json["data"]
    entry = client.post(
        "/api/knowledge/entries",
        headers=headers,
        json={"title": "Note 1", "content": "Content", "tags": ["tag1"], "topic_id": topic["id"]},
    ).json["data"]
    return entry["id"]


def test_create_and_list_study_logs(client, auth_headers):
    entry_id = _create_entry(client, auth_headers)
    create_resp = client.post("/api/study/logs", headers=auth_headers, json={"entry_id": entry_id, "note": "Today"})
    assert create_resp.status_code == HTTPStatus.OK
    log_id = create_resp.json["data"]["id"]

    list_resp = client.get("/api/study/logs", headers=auth_headers)
    assert list_resp.status_code == HTTPStatus.OK
    assert list_resp.json["data"]["total"] >= 1
    assert any(item["id"] == log_id for item in list_resp.json["data"]["items"])
