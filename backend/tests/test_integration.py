from fastapi.testclient import TestClient

from app.main import create_app


def test_validation_and_safe_errors(tmp_path):
    with TestClient(create_app(f"sqlite:///{tmp_path}/test.db")) as c:
        assert c.post("/api/v1/sessions", json={"question": "x"}).status_code == 422
        assert c.get("/api/v1/sessions/missing").json()["error"]["code"] == "HTTP_404"
        bad = {
            "name": "x",
            "version": "1",
            "provenance": "x",
            "verified": True,
            "questions": [{"id": "1", "question": "abc", "answer": "a", "source_url": "javascript:alert(1)"}],
        }
        assert c.post("/api/v1/datasets/import", json=bad).status_code == 422
        bad["questions"][0]["source_url"] = ""
        bad["questions"] *= 2
        assert c.post("/api/v1/datasets/import", json=bad).status_code == 422


def test_persistence_and_live_failure(tmp_path, monkeypatch):
    for name in (
        "ALEM_API_KEY",
        "ALEM_API_KEY_TOLE",
        "ALEM_API_KEY_KAZYBEK",
        "ALEM_API_KEY_AITEKE",
        "ALEM_MODEL",
        "ALEM_MODEL_TOLE",
        "ALEM_MODEL_KAZYBEK",
        "ALEM_MODEL_AITEKE",
    ):
        monkeypatch.delenv(name, raising=False)
    url = f"sqlite:///{tmp_path}/test.db"
    with TestClient(create_app(url)) as c:
        s = c.post("/api/v1/sessions", json={"question": "A live question", "mode": "live"}).json()
        c.post("/api/v1/sessions/" + s["id"] + "/start")
        result = c.get("/api/v1/sessions/" + s["id"]).json()
        assert result["status"] == "failed"
        assert "Configure" in result["error"]
        assert c.post("/api/v1/sessions/" + s["id"] + "/start").status_code == 409
        assert c.post("/api/v1/models/test").json()["ok"] is False
    with TestClient(create_app(url)) as c:
        assert c.get("/api/v1/sessions/" + s["id"]).json()["error"] == result["error"]
        assert c.get("/api/v1/exports/sessions/" + s["id"]).status_code == 200


def test_restart_retains_partial_work_and_emits_failed(tmp_path):
    from app.engine import new_session
    from app.storage import Store

    url = f"sqlite:///{tmp_path}/restart.db"
    store = Store(url)
    s = new_session(
        {
            "question": "Interrupted question",
            "mode": "demo",
            "language": "en",
            "rounds": 1,
            "evidence_enabled": False,
            "domain": "general",
        }
    )
    store.event(s, "revision", "running")
    with TestClient(create_app(url)) as c:
        assert c.get("/api/v1/sessions/" + s["id"]).json()["status"] == "failed"
        assert "failed" in c.get("/api/v1/sessions/" + s["id"] + "/events").text
