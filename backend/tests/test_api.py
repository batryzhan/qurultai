from fastapi.testclient import TestClient

from app.main import create_app


def test_session_flow(tmp_path):
    with TestClient(create_app(f"sqlite:///{tmp_path}/test.db")) as c:
        assert c.get("/api/v1/health").json() == {"status": "ok"}
        s = c.post(
            "/api/v1/sessions",
            json={
                "question": "What is evidence?",
                "mode": "demo",
                "language": "en",
                "rounds": 1,
                "evidence_enabled": True,
                "domain": "science",
            },
        ).json()
        assert c.post(f"/api/v1/sessions/{s['id']}/start").status_code == 202
        s = c.get(f"/api/v1/sessions/{s['id']}").json()
        assert s["status"] == "completed"
        assert len(s["arguments"]) == 9
        assert s["simulated"] is True
        assert s["synthesis"]["answer"]
        assert "completed" in c.get(f"/api/v1/sessions/{s['id']}/events").text


def test_benchmark(tmp_path):
    with TestClient(create_app(f"sqlite:///{tmp_path}/test.db")) as c:
        d = c.post(
            "/api/v1/datasets/import",
            json={
                "name": "fixture",
                "version": "1",
                "provenance": "test",
                "verified": True,
                "questions": [
                    {
                        "id": "q1",
                        "question": "What is 2 + 2?",
                        "answer": "4",
                        "category": "math",
                        "source_url": "",
                    }
                ],
            },
        ).json()
        r = c.post(
            "/api/v1/benchmarks",
            json={
                "dataset_id": d["id"],
                "mode": "demo",
                "strategies": ["single", "majority", "debate"],
                "repetitions": 1,
            },
        ).json()
        r = c.get("/api/v1/benchmarks/" + r["id"]).json()
        assert r["status"] == "completed"
        assert len(r["results"]) == 3
        assert r["metrics"]["single"]["accuracy"] == 1
        assert "question_id" in c.get("/api/v1/exports/benchmarks/" + r["id"] + "?format=csv").text
