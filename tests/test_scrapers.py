from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.data.scrapers.funding import _amount_usd, _funding_impact, get_funding_signals
from backend.data.scrapers.jobs import get_job_signals
from backend.data.scrapers.news import get_news_signals


def test_jobs_returns_signals_for_notion():
    out = get_job_signals(["Notion"])
    assert out
    assert all(s.source == "job_postings" for s in out)
    assert all(s.company == "Notion" for s in out)
    assert any("hiring" in s.title for s in out)


def test_jobs_partial_match_case_insensitive():
    out = get_job_signals(["not"])
    assert any("Notion" in s.company for s in out)


def test_funding_returns_linear_and_impact():
    out = get_funding_signals(["Linear"])
    assert len(out) == 1
    s = out[0]
    assert s.source == "funding"
    assert "35M" in s.title
    assert s.impact == "medium"


def test_funding_high_impact_over_50m():
    assert _funding_impact("$50M") == "high"
    assert _funding_impact("$49M") == "medium"
    assert _amount_usd("$275M") == 275_000_000


def test_funding_json_loads():
    path = Path(__file__).resolve().parents[1] / "backend" / "data" / "mock" / "funding.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert len(data) >= 15
    assert {row["company"] for row in data if row["company"] == "Linear"} == {"Linear"}


def test_news_fallback_without_api_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    out = get_news_signals(["Acme Corp"])
    assert len(out) == 3
    assert {s.source for s in out} == {"news"}
    assert all(s.company == "Acme Corp" for s in out)


def test_news_parses_gnews_payload(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("NEWS_API_KEY", "test-token")

    class FakeResp:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "articles": [
                    {
                        "title": "Acme Corp acquires smaller rival in cloud push",
                        "description": "A longer description " * 20,
                        "publishedAt": "2025-04-01T12:00:00Z",
                    }
                ]
            }

    def fake_get(url: str, timeout: int | None = None) -> FakeResp:
        assert "gnews.io" in url
        assert "Acme" in url or "Acme%20Corp" in url
        return FakeResp()

    monkeypatch.setattr("backend.data.scrapers.news.requests.get", fake_get)
    out = get_news_signals(["Acme Corp"])
    assert len(out) == 1
    assert out[0].impact == "high"
    assert "acquires" in out[0].title.lower()
    assert len(out[0].body) <= 200
    assert out[0].date == "2025-04-01"


def test_all_scrapers_together_notation_and_linear(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    names = ["Notion", "Linear"]
    news = get_news_signals(names)
    jobs = get_job_signals(names)
    funding = get_funding_signals(names)
    merged = news + jobs + funding
    sources = {s.source for s in merged}
    assert sources == {"news", "job_postings", "funding"}
    assert len(merged) >= 10
