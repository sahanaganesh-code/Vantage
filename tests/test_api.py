from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_root_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_signals_stub_mode(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USE_API_STUBS", "1")
    r = client.get("/api/v1/signals", params={"competitors": "Notion"})
    assert r.status_code == 200
    assert r.json()["stub"] is True


def test_signals_live_uses_processor(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("USE_API_STUBS", raising=False)
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    r = client.get("/api/v1/signals", params={"company_name": "Us", "competitors": "Notion"})
    assert r.status_code == 200
    body = r.json()
    assert body["stub"] is False
    assert body["signals"]
    kinds = {s["source"] for s in body["signals"]}
    assert kinds <= {"news", "job_postings", "funding"}


def test_jobs_route_wires_scraper(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("USE_API_STUBS", raising=False)
    r = client.get("/api/v1/jobs", params={"competitors": "Linear"})
    assert r.status_code == 200
    body = r.json()
    assert body["stub"] is False
    assert all(j["source"] == "job_postings" for j in body["jobs"])


def test_agent_stub_mode(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USE_API_STUBS", "1")
    r = client.post(
        "/api/v1/agent/analyze",
        json={"company_name": "Co", "competitors": ["Notion"], "query": "What matters?"},
    )
    assert r.status_code == 200
    assert r.json()["stub"] is True


def test_agent_live_without_openai_returns_fallback(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("USE_API_STUBS", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    r = client.post(
        "/api/v1/agent/analyze",
        json={"company_name": "Co", "competitors": ["Notion"], "query": "Summarize hiring."},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["mock"] is True
    assert body["job_signals_used"] >= 1


def test_agent_live_calls_openai_when_configured(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("USE_API_STUBS", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    class FakeMessage:
        content = "Synthetic analysis from unit test."

    class FakeChoice:
        message = FakeMessage()

    class FakeCompletion:
        choices = [FakeChoice()]

    class FakeCompletions:
        def create(self, **kwargs):
            return FakeCompletion()

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        chat = FakeChat()

    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setattr("openai.OpenAI", lambda *a, **k: FakeClient())

    r = client.post(
        "/api/v1/agent/analyze",
        json={"company_name": "Co", "competitors": ["Notion"], "query": "Test"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["mock"] is False
    assert "Synthetic analysis" in body["analysis"]
