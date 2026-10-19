import httpx
import pytest

from app.engine import disagreements, evidence
from app.metrics import majority, metrics, normalize
from app.providers import Provider, ProviderError, prompt


def test_metrics_known_cases():
    rows = [
        {"is_correct": True, "confidence": 0.8, "error": None, "latency_ms": 10},
        {"is_correct": False, "confidence": 0.4, "error": None, "latency_ms": 30},
    ]
    m = metrics(rows)
    assert m["accuracy"] == 0.5
    assert m["brier_score"] == pytest.approx(0.1)
    assert m["ece"] == pytest.approx(0.3)
    assert m["mean_latency_ms"] == 20
    assert metrics([])["accuracy"] is None
    assert metrics([{**rows[0], "confidence": None}])["ece"] is None


def test_majority_tie_and_normalization():
    assert normalize("  FOUR. ") == "four"
    assert majority([{"answer": "a", "content": "a"}, {"answer": "b", "content": "b"}])["answer"] == "ABSTAIN"
    assert (
        majority(
            [
                {"answer": "A", "content": "A"},
                {"answer": " a. ", "content": "a"},
                {"answer": "b", "content": "b"},
            ]
        )["answer"]
        == "A"
    )


def test_no_fabricated_conflicts_and_sources():
    assert disagreements([]) == []
    assert evidence("unrelated question") == []
    assert evidence("transformer attention")[0]["verification_status"] == "retrieved_unverified"
    args = [
        {"stage": "initial_arguments", "answer": a, "agent": str(i), "id": str(i)}
        for i, a in enumerate(["yes", "no"])
    ]
    assert disagreements(args)[0]["argument_ids"] == ["0", "1"]
    assert "untrusted" in prompt("tole", "test", "revision", [], "en")[0]["content"]


@pytest.mark.parametrize(
    "status,body,code",
    [
        (401, {}, "LLM_PROVIDER_HTTP"),
        (200, {"choices": []}, "LLM_PROVIDER_RESPONSE"),
        (
            200,
            {"choices": [{"message": {"content": '{"content":"x","confidence":2}'}}]},
            "LLM_PROVIDER_RESPONSE",
        ),
    ],
)
async def test_provider_errors(monkeypatch, status, body, code):
    monkeypatch.setenv("ALEM_API_KEY", "secret-not-for-errors")
    for agent in ("TOLE", "KAZYBEK", "AITEKE"):
        monkeypatch.setenv("ALEM_MODEL_" + agent, "test-configured-id")
    provider = Provider("live", httpx.MockTransport(lambda request: httpx.Response(status, json=body)))
    with pytest.raises(ProviderError) as exc:
        await provider.ask("tole", "question", "initial")
    assert exc.value.code == code
    assert "secret" not in str(exc.value)


async def test_provider_timeout(monkeypatch):
    monkeypatch.setenv("ALEM_API_KEY", "test")
    for agent in ("TOLE", "KAZYBEK", "AITEKE"):
        monkeypatch.setenv("ALEM_MODEL_" + agent, "configured")

    def handler(request):
        raise httpx.ReadTimeout("sensitive details")

    with pytest.raises(ProviderError, match="timed out"):
        await Provider("live", httpx.MockTransport(handler)).ask("tole", "question", "initial")


async def test_provider_valid_usage(monkeypatch):
    monkeypatch.setenv("ALEM_API_KEY", "test")
    for agent in ("TOLE", "KAZYBEK", "AITEKE"):
        monkeypatch.setenv("ALEM_MODEL_" + agent, "configured")
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": '{"content":"Reason","answer":"4","confidence":0.7}'}}],
                "usage": {"total_tokens": 17},
            },
        )
    )
    reply = await Provider("live", transport).ask("tole", "question", "initial")
    assert reply["token_usage"] == 17
    assert reply["model"] == "configured"


async def test_provider_uses_role_specific_keys_and_models(monkeypatch):
    from app.schemas import configuration

    monkeypatch.delenv("ALEM_API_KEY", raising=False)
    expected = {"tole": ("key-tole", "qwen3-8"), "kazybek": ("key-kazybek", "gemma4"), "aiteke": ("key-aiteke", "gpt-oss")}
    for role, (key, model) in expected.items():
        monkeypatch.setenv(f"ALEM_API_KEY_{role.upper()}", key)
        monkeypatch.setenv(f"ALEM_MODEL_{role.upper()}", model)
    assert configuration()["configured"]

    for role, (key, model) in expected.items():
        seen = {}

        def handler(request, seen=seen):
            seen["authorization"] = request.headers["authorization"]
            seen["model"] = request.read().decode()
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": '{"content":"Reason","answer":"4"}'}}]},
            )

        reply = await Provider("live", httpx.MockTransport(handler)).ask(role, "question", "initial")
        assert seen["authorization"] == f"Bearer {key}"
        assert f'"model":"{model}"' in seen["model"]
        assert reply["model"] == model


def test_config_fallback_and_unsafe_endpoint(monkeypatch):
    from app.schemas import configuration

    monkeypatch.setenv("ALEM_MODEL", "common-configured-model")
    monkeypatch.setenv("ALEM_API_KEY", "secret")
    monkeypatch.delenv("ALEM_ENDPOINT", raising=False)
    monkeypatch.setenv("ALEM_BASE_URL", "https://llm.alem.ai/v1")
    for a in ("TOLE", "KAZYBEK", "AITEKE"):
        monkeypatch.setenv("ALEM_MODEL_" + a, "")
    assert configuration()["configured"]
    assert configuration()["models"]["tole"] == "common-configured-model"
    monkeypatch.setenv("ALEM_ENDPOINT", "https://secret:password@example.com/chat?api_key=secret")
    assert not configuration()["configured"]
    assert "secret" not in configuration()["endpoint"]


async def test_incremental_context_and_token_accounting(tmp_path):
    from app.engine import new_session, run_council
    from app.storage import Store

    calls = []
    synthesis_context = []

    class RecordedProvider:
        async def ask(self, agent, question, stage, context, language):
            calls.append((agent, stage, len(context)))
            if stage == "synthesis":
                synthesis_context.extend(context)
            return {
                "content": "reasoned response",
                "answer": agent if stage == "initial_arguments" else "4",
                "confidence": 0.7,
                "model": "test-only",
                "token_usage": 5,
            }

    store = Store(f"sqlite:///{tmp_path}/test.db")
    s = new_session(
        {
            "question": "A test question",
            "mode": "live",
            "language": "en",
            "rounds": 1,
            "evidence_enabled": False,
            "domain": "test",
        }
    )
    store.event(s, "created", "created")
    await run_council(store, s, RecordedProvider())
    assert s["status"] == "completed"
    assert all(n == 0 for a, stage, n in calls if stage == "initial_arguments")
    assert all(n == 3 for a, stage, n in calls if stage == "cross_examination")
    assert len(s["arguments"]) == 9
    assert s["disagreements"][0]["classification"] == "answer_difference"
    assert s["synthesis"]["final_answer"] == "4"
    assert any(item.get("classification") == "answer_difference" for item in synthesis_context)
    assert [e["stage"] for e in store.events(s["id"])][-1] == "completed"


def test_stage_directives_and_frozen_prompt_metadata():
    from app.engine import benchmark_config
    from app.providers import PROMPT_VERSION, ROLES

    initial = prompt("tole", "question", "initial_arguments", [], "en")[0]["content"]
    cross = prompt("tole", "question", "cross_examination", [], "en")[0]["content"]
    revision = prompt("tole", "question", "revision", [], "en")[0]["content"]
    synthesis = prompt("tole", "question", "synthesis", [], "en")[0]["content"]
    assert "without assuming peer conclusions" in initial
    assert "specific peer claims" in cross and "Do not manufacture disagreement" in cross
    assert "changed conclusions" in revision and "remaining uncertainties" in revision
    assert "Preserve unresolved disagreements" in synthesis
    assert "source IDs or URLs" in synthesis and "new propositions" in synthesis
    assert PROMPT_VERSION == "council-v2"
    config = benchmark_config({"mode": "demo"}, {"version": "1", "verified": False})
    frozen = config["prompt_snapshot"]
    assert frozen["version"] == PROMPT_VERSION
    assert len(frozen["sha256"]) == 64
    assert frozen["roles"] == ROLES
    original = ROLES["tole"]
    try:
        ROLES["tole"] = "Changed after experiment configuration"
        assert frozen["roles"]["tole"] == original
    finally:
        ROLES["tole"] = original
