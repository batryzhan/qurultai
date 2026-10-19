import os
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

AGENTS = ("tole", "kazybek", "aiteke")


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SessionInput(Strict):
    question: str = Field(min_length=3, max_length=8000)
    mode: Literal["demo", "live"] = "demo"
    language: Literal["kk", "ru", "en"] = "kk"
    rounds: int = Field(default=1, ge=1, le=3)
    evidence_enabled: bool = True
    domain: str = Field(default="general", max_length=100)


class Question(Strict):
    id: str = Field(min_length=1, max_length=100)
    question: str = Field(min_length=3, max_length=8000)
    answer: str = Field(min_length=1, max_length=2000)
    category: str = Field(default="general", max_length=100)
    source_url: str = Field(default="", max_length=2000)

    @field_validator("source_url")
    @classmethod
    def url(cls, v):
        if v:
            HttpUrl(v)
        return v


class DatasetInput(Strict):
    name: str = Field(min_length=1, max_length=200)
    version: str = Field(min_length=1, max_length=100)
    provenance: str = Field(min_length=1, max_length=4000)
    verified: bool = False
    questions: list[Question] = Field(min_length=1, max_length=100)

    @field_validator("questions")
    @classmethod
    def unique(cls, v):
        if len({q.id for q in v}) != len(v):
            raise ValueError("Question IDs must be unique")
        return v


class BenchmarkInput(Strict):
    dataset_id: str
    mode: Literal["demo", "live"] = "demo"
    strategies: list[Literal["single", "majority", "debate"]] = Field(min_length=1, max_length=3)
    repetitions: Literal[1] = 1

    @field_validator("strategies")
    @classmethod
    def unique(cls, v):
        if len(set(v)) != len(v):
            raise ValueError("Strategies must be unique")
        return v


def configuration():
    from urllib.parse import urlsplit

    endpoint = os.getenv("ALEM_ENDPOINT") or (
        os.getenv("ALEM_BASE_URL", "https://llm.alem.ai/v1").rstrip("/") + "/chat/completions"
    )
    parsed = urlsplit(endpoint)
    safe = (
        parsed.scheme == "https"
        and bool(parsed.hostname)
        and not parsed.username
        and not parsed.password
        and not parsed.query
        and not parsed.fragment
    )
    models = {a: os.getenv("ALEM_MODEL_" + a.upper()) or os.getenv("ALEM_MODEL", "") for a in AGENTS}
    key_configured = {
        a: bool(os.getenv("ALEM_API_KEY_" + a.upper()) or os.getenv("ALEM_API_KEY")) for a in AGENTS
    }
    return {
        "configured": bool(safe and all(key_configured.values()) and all(models.values())),
        "endpoint": endpoint if safe else "https://llm.alem.ai/v1/chat/completions",
        "models": models,
        "key_configured": key_configured,
        "simulated_available": True,
    }
