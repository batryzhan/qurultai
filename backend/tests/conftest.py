import pytest


@pytest.fixture(autouse=True)
def isolate_provider_credentials(monkeypatch):
    """Do not let a developer's local .env affect tests or issue live requests."""
    for name in (
        "ALEM_API_KEY",
        "ALEM_API_KEY_TOLE",
        "ALEM_API_KEY_KAZYBEK",
        "ALEM_API_KEY_AITEKE",
        "ALEM_MODEL",
        "ALEM_MODEL_TOLE",
        "ALEM_MODEL_KAZYBEK",
        "ALEM_MODEL_AITEKE",
        "ALEM_ENDPOINT",
    ):
        monkeypatch.delenv(name, raising=False)
