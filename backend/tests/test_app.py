from http import HTTPStatus


def test_testing_config(app):
    assert app.config["TESTING"] is True
    assert app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite")
    assert app.config["SCHEDULER_ENABLED"] is False


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == HTTPStatus.OK
    assert resp.json == {"status": "ok"}


def test_test_routes_ok_and_error(client):
    ok_resp = client.get("/_test_ok")
    assert ok_resp.status_code == HTTPStatus.OK
    assert ok_resp.json["code"] == 0

    err_resp = client.get("/_test_error")
    assert err_resp.status_code == 418
    assert err_resp.json["code"] == 4001
    assert err_resp.json["message"] == "boom"
