from __future__ import annotations

from datetime import date
from typing import Any


def get_signals_for_company(company: str) -> list[dict[str, Any]]:
    """Return demo market signals for the given company (hackathon / dev stub)."""
    today = date.today().isoformat()
    safe = company.strip() or "your company"
    return [
        {
            "source": "news",
            "title": f"Category momentum around {safe}",
            "body": (
                f"Trade press highlights rising budgets in segments where {safe} competes; "
                "buyers are re-evaluating incumbents ahead of Q planning."
            ),
            "impact": "high",
            "date": today,
        },
        {
            "source": "reviews",
            "title": "Peer review themes: onboarding friction",
            "body": (
                "Aggregated G2-style feedback cites implementation timelines and "
                "integrations as the top pain for alternatives in this space."
            ),
            "impact": "medium",
            "date": today,
        },
        {
            "source": "hiring",
            "title": "Competitor GTM expansion signals",
            "body": (
                "Multiple open roles in enterprise AE and sales engineering suggest "
                "a push upmarket within the next two quarters."
            ),
            "impact": "medium",
            "date": today,
        },
        {
            "source": "product",
            "title": "Feature velocity on core workflow",
            "body": (
                "Public changelog activity shows weekly releases focused on automation "
                "and API coverage—likely targeting mid-market land-and-expand."
            ),
            "impact": "high",
            "date": today,
        },
        {
            "source": "finance",
            "title": "Vendor consolidation chatter",
            "body": (
                "Analyst notes mention CFO-led stack reviews; multi-year contracts "
                "may be vulnerable where ROI proof is thin."
            ),
            "impact": "low",
            "date": today,
        },
    ]
