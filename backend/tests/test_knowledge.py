from http import HTTPStatus

import pytest


@pytest.fixture
def auth_headers(client):
    resp = client.post("/api/auth/register", json={"email": "k1@example.com", "password": "Secret123!"})
    token = resp.json["data"]["tokens"]["access"]
    return {"Authorization": f"Bearer {token}"}


def test_topics_and_entries_crud(client, auth_headers):
    # create topic
    t_resp = client.post("/api/knowledge/topics", headers=auth_headers, json={"name": "Math", "desc": "Algebra"})
    assert t_resp.status_code == HTTPStatus.OK
    topic_id = t_resp.json["data"]["id"]

    # list topics
    list_resp = client.get("/api/knowledge/topics", headers=auth_headers)
    assert list_resp.status_code == HTTPStatus.OK
    assert list_resp.json["data"]["total"] == 1

    # create entry
    e_resp = client.post(
        "/api/knowledge/entries",
        headers=auth_headers,
        json={"title": "Group Theory", "content": "Definition...", "tags": ["math"], "topic_id": topic_id},
    )
    assert e_resp.status_code == HTTPStatus.OK
    entry_id = e_resp.json["data"]["id"]

    # list entries filter by keyword
    list_entries = client.get("/api/knowledge/entries", headers=auth_headers, query_string={"keyword": "Group"})
    assert list_entries.status_code == HTTPStatus.OK
    assert list_entries.json["data"]["total"] == 1

    # update entry
    up_resp = client.put(
        f"/api/knowledge/entries/{entry_id}",
        headers=auth_headers,
        json={"title": "Group Theory Updated", "tags": ["math", "algebra"]},
    )
    assert up_resp.status_code == HTTPStatus.OK
    assert "Updated" in up_resp.json["data"]["title"]

    # delete entry
    del_resp = client.delete(f"/api/knowledge/entries/{entry_id}", headers=auth_headers)
    assert del_resp.status_code == HTTPStatus.OK
