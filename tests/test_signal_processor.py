from __future__ import annotations

import pytest

from backend.data.processors.signal_processor import (
    get_signals_for_company,
    get_signals_for_competitor,
)
from backend.data.models import Signal


def test_processor_dedupes_exact_titles(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("NEWS_API_KEY", raising=False)

    def fake_news(names: list[str]):
        return [
            Signal(
                source="news",
                title="Duplicate headline",
                body="a",
                impact="medium",
                date="2025-03-01",
                company=names[0],
                tags=[],
            ),
            Signal(
                source="news",
                title="Duplicate headline",
                body="b",
                impact="high",
                date="2025-03-02",
                company=names[0],
                tags=[],
            ),
        ]

    monkeypatch.setattr(
        "backend.data.processors.signal_processor.get_news_signals",
        fake_news,
    )
    monkeypatch.setattr(
        "backend.data.processors.signal_processor.get_job_signals",
        lambda _: [],
    )
    monkeypatch.setattr(
        "backend.data.processors.signal_processor.get_funding_signals",
        lambda _: [],
    )

    out = get_signals_for_company("Us", ["SoloCo"])
    assert len(out) == 1
    assert out[0].title == "Duplicate headline"


def test_processor_caps_at_thirty(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    out = get_signals_for_company("X", ["Notion", "Linear", "Figma", "Asana"])
    assert len(out) <= 30


def test_processor_impact_then_recency_order(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "backend.data.processors.signal_processor.get_news_signals",
        lambda _: [],
    )
    monkeypatch.setattr(
        "backend.data.processors.signal_processor.get_job_signals",
        lambda _: [],
    )
    monkeypatch.setattr(
        "backend.data.processors.signal_processor.get_funding_signals",
        lambda _: [
            Signal(
                source="funding",
                title="Old medium",
                body="",
                impact="medium",
                date="2024-01-01",
                company="Co",
                tags=[],
            ),
            Signal(
                source="funding",
                title="Newer medium",
                body="",
                impact="medium",
                date="2025-01-01",
                company="Co",
                tags=[],
            ),
            Signal(
                source="funding",
                title="Old high",
                body="",
                impact="high",
                date="2024-06-01",
                company="Co",
                tags=[],
            ),
        ],
    )
    out = get_signals_for_company("", ["Co"])
    titles = [s.title for s in out]
    assert titles[0] == "Old high"
    assert titles[1] == "Newer medium"
    assert titles[2] == "Old medium"


def test_get_signals_for_competitor_alias():
    out = get_signals_for_competitor("Notion")
    assert out
    assert all(s.company == "Notion" or "Notion" in s.title for s in out[:5])
