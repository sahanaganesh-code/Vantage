from __future__ import annotations

from backend.data.models import Signal
from backend.data.scrapers.funding import get_funding_signals
from backend.data.scrapers.jobs import get_job_signals
from backend.data.scrapers.news import get_news_signals


def get_signals_for_company(company_name: str, competitors: list[str]) -> list[Signal]:
    """
    Aggregate signals for a company's competitive context.

    Pulls from all scrapers, deduplicates, and ranks by impact + recency.

    Note: `company_name` is reserved for future scoping; monitoring currently uses `competitors`.
    """
    _ = company_name
    all_targets = competitors  # monitor competitors
    all_signals: list[Signal] = []

    all_signals += get_news_signals(all_targets)
    all_signals += get_job_signals(all_targets)
    all_signals += get_funding_signals(all_targets)

    seen_titles: set[str] = set()
    deduped: list[Signal] = []
    for s in all_signals:
        if s.title not in seen_titles:
            seen_titles.add(s.title)
            deduped.append(s)

    impact_order = {"high": 0, "medium": 1, "low": 2}
    # Stable sorts: newest first, then reorder by impact while preserving date order within ties.
    deduped.sort(key=lambda x: x.date, reverse=True)
    deduped.sort(key=lambda s: impact_order[s.impact])

    return deduped[:30]


def get_signals_for_competitor(competitor: str) -> list[Signal]:
    return get_signals_for_company("", [competitor])
