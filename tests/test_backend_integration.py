from __future__ import annotations

import json

import pytest

from backend.data.models import Company
from backend.signals_service import (
    get_signals_for_company_model,
    get_signals_for_company_payload,
)


def test_signals_service_returns_models(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    company = Company(
        name="VantageCo",
        competitors=["Notion", "Linear"],
        accounts=["acct_001"],
    )
    signals = get_signals_for_company_model(company)
    assert signals
    assert len(signals) <= 30
    kinds = {s.source for s in signals}
    assert kinds <= {"news", "job_postings", "funding"}


def test_signals_service_payload_is_json_safe(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    company = Company(name="VantageCo", competitors=["Figma"], accounts=[])
    payload = get_signals_for_company_payload(company)
    assert isinstance(payload, list)
    assert payload[0]["source"] in ("news", "job_postings", "funding")
    assert payload[0]["impact"] in ("high", "medium", "low")
    json_roundtrip = json.dumps(payload)
    assert "Figma" in json_roundtrip
