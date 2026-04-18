from __future__ import annotations

import os
from datetime import datetime
from typing import Final
from urllib.parse import quote_plus

import requests
from dotenv import load_dotenv

from backend.data.models import Signal

load_dotenv()

_GNEWS_URL: Final[str] = "https://gnews.io/api/v4/search"
_HIGH_IMPACT_TITLE_KEYWORDS: Final[tuple[str, ...]] = (
    "launch",
    "raises",
    "acquires",
    "cuts",
    "layoffs",
)
_TAG_KEYWORDS: Final[tuple[str, ...]] = (
    "ai",
    "ml",
    "cloud",
    "security",
    "funding",
    "acquisition",
    "ipo",
    "enterprise",
    "product",
    "layoff",
    "partnership",
    "data",
    "api",
    "platform",
    "revenue",
    "growth",
    "saas",
    "software",
)


def _published_to_date(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return datetime.utcnow().date().isoformat()
    try:
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(value).date().isoformat()
    except ValueError:
        return value[:10] if len(value) >= 10 else datetime.utcnow().date().isoformat()


def _impact_from_title(title: str) -> str:
    t = title.lower()
    if any(k in t for k in _HIGH_IMPACT_TITLE_KEYWORDS):
        return "high"
    return "medium"


def _tags_from_title(title: str) -> list[str]:
    t = title.lower()
    return [kw for kw in _TAG_KEYWORDS if kw in t]


def _mock_news_signals(company_names: list[str]) -> list[Signal]:
    out: list[Signal] = []
    for company in company_names:
        out.extend(
            [
                Signal(
                    source="news",
                    title=f"{company} expands AI assistant capabilities for enterprise teams",
                    body=(
                        f"Coverage indicates {company} is shipping assistant features aimed at "
                        "larger accounts, with a focus on permissions and auditability."
                    )[:200],
                    impact="high",
                    date="2025-03-12",
                    company=company,
                    tags=["ai", "enterprise", "product"],
                ),
                Signal(
                    source="news",
                    title=f"{company} announces new partnership to accelerate go-to-market",
                    body=(
                        f"Partners are positioning {company} alongside broader cloud marketplaces, "
                        "suggesting co-sell momentum in mid-market and enterprise."
                    )[:200],
                    impact="medium",
                    date="2025-03-05",
                    company=company,
                    tags=["partnership", "growth", "saas"],
                ),
                Signal(
                    source="news",
                    title=f"Analysts weigh in on {company}'s product velocity versus peers",
                    body=(
                        "Analyst commentary highlights roadmap execution and packaging changes as "
                        f"key variables for {company} over the next two quarters."
                    )[:200],
                    impact="medium",
                    date="2025-02-20",
                    company=company,
                    tags=["product", "growth", "saas"],
                ),
            ]
        )
    return out


def get_news_signals(company_names: list[str]) -> list[Signal]:
    key = (os.getenv("NEWS_API_KEY") or "").strip()
    if not key or not company_names:
        return _mock_news_signals(company_names)

    signals: list[Signal] = []
    for company in company_names:
        q = quote_plus(company)
        url = f"{_GNEWS_URL}?q={q}&token={key}&lang=en&max=5"
        try:
            resp = requests.get(url, timeout=12)
            resp.raise_for_status()
            payload = resp.json()
        except (requests.RequestException, ValueError):
            signals.extend(_mock_news_signals([company]))
            continue

        articles = payload.get("articles") or []
        if not articles:
            signals.extend(_mock_news_signals([company]))
            continue

        for article in articles:
            title = (article.get("title") or "").strip() or f"{company} in the news"
            description = (article.get("description") or "").strip()
            body = description[:200] if description else ""
            published = article.get("publishedAt") or article.get("published_at") or ""
            signals.append(
                Signal(
                    source="news",
                    title=title,
                    body=body,
                    impact=_impact_from_title(title),
                    date=_published_to_date(str(published)),
                    company=company,
                    tags=_tags_from_title(title),
                )
            )

    return signals
