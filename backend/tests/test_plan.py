from http import HTTPStatus

import pytest


@pytest.fixture
def auth_headers(client):
    resp = client.post("/api/auth/register", json={"email": "plan@example.com", "password": "Secret123!"})
    token = resp.json["data"]["tokens"]["access"]
    return {"Authorization": f"Bearer {token}"}


def test_plan_crud_and_tasks_flow(client, auth_headers):
    # create plan
    create_resp = client.post(
        "/api/plans",
        headers=auth_headers,
        json={"title": "Test Plan", "goal": "Ship v1", "priority": "high", "tags": ["p0"], "status": "not_started"},
    )
    assert create_resp.status_code == HTTPStatus.OK
    plan_id = create_resp.json["data"]["id"]

    # list plans
    list_resp = client.get("/api/plans", headers=auth_headers)
    assert list_resp.status_code == HTTPStatus.OK
    assert list_resp.json["data"]["total"] == 1

    # create task
    task_resp = client.post(
        f"/api/plans/{plan_id}/tasks",
        headers=auth_headers,
        json={"title": "Task 1", "estimate_minutes": 60, "priority": "high"},
    )
    assert task_resp.status_code == HTTPStatus.OK
    task_id = task_resp.json["data"]["id"]

    # complete task
    complete_resp = client.post(f"/api/tasks/{task_id}/complete", headers=auth_headers)
    assert complete_resp.status_code == HTTPStatus.OK
    assert complete_resp.json["data"]["status"] == "done"

    # detail should show progress 1
    detail_resp = client.get(f"/api/plans/{plan_id}", headers=auth_headers)
    assert detail_resp.status_code == HTTPStatus.OK
    assert detail_resp.json["data"]["progress"] == pytest.approx(1.0)
    assert detail_resp.json["data"]["tasks"][0]["status"] == "done"

    # update plan
    update_resp = client.put(f"/api/plans/{plan_id}", headers=auth_headers, json={"title": "Plan Updated"})
    assert update_resp.status_code == HTTPStatus.OK
    assert update_resp.json["data"]["title"] == "Plan Updated"

    # delete plan
    del_resp = client.delete(f"/api/plans/{plan_id}", headers=auth_headers)
    assert del_resp.status_code == HTTPStatus.OK
