from __future__ import annotations

import os
import re
import string
from typing import Final, Literal

import requests
from dotenv import load_dotenv
from urllib.parse import quote_plus

from backend.data.models import Signal

load_dotenv()

_GNEWS_URL: Final[str] = "https://gnews.io/api/v4/search"
_HIGH_IMPACT = re.compile(
    r"\b(launch|raises|acquires|cuts|layoffs|breach)\b",
    re.IGNORECASE,
)


def _tags_from_title(title: str) -> list[str]:
    """Words over 4 chars with a leading capital letter (Person 1 spec)."""
    tags: list[str] = []
    for raw in title.split():
        word = raw.strip(string.punctuation)
        if len(word) > 4 and word[0].isupper():
            tags.append(word)
    return tags


def _clip(text: str | None, max_len: int) -> str:
    if not text:
        return ""
    return text.strip()[:max_len]


def _impact_for_title(title: str) -> Literal["high", "medium"]:
    return "high" if _HIGH_IMPACT.search(title) else "medium"


def _published_date(published: str) -> str:
    published = (published or "").strip()
    if len(published) >= 10:
        return published[:10]
    return "1970-01-01"


def _fallback_signals(company: str) -> list[Signal]:
    """Hardcoded demo signals when the key is missing or the GNews request fails."""
    return [
        Signal(
            source="news",
            title=f"{company} expands enterprise offering",
            body="Company announces new enterprise tier targeting Fortune 500 customers.",
            impact="medium",
            date="2025-04-01",
            company=company,
            tags=["enterprise", "growth"],
        ),
        Signal(
            source="news",
            title=f"{company} raises Series C",
            body="Funding round led by top-tier VCs to accelerate product development.",
            impact="high",
            date="2025-03-15",
            company=company,
            tags=["funding"],
        ),
        Signal(
            source="news",
            title=f"{company} launches AI features",
            body="New AI-powered capabilities announced at annual product conference.",
            impact="high",
            date="2025-03-01",
            company=company,
            tags=["AI", "product"],
        ),
    ]


def get_news_signals(company_names: list[str]) -> list[Signal]:
    """
    GNews-backed signals per company. Uses requests.get (see tests monkeypatch).

    Fallback (exactly three demo rows per company) applies when NEWS_API_KEY is
    missing/blank or the HTTP request / JSON parsing fails. Successful responses
    with zero articles return no synthetic rows (Person 1 spec).
    """
    key = (os.getenv("NEWS_API_KEY") or "").strip()
    if not key or not company_names:
        out: list[Signal] = []
        for company in company_names:
            name = (company or "").strip()
            if name:
                out.extend(_fallback_signals(name))
        return out

    signals: list[Signal] = []
    for company in company_names:
        name = (company or "").strip()
        if not name:
            continue

        q = quote_plus(name)
        url = f"{_GNEWS_URL}?q={q}&token={key}&lang=en&max=5"
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            payload = resp.json()
        except (requests.RequestException, ValueError, TypeError):
            signals.extend(_fallback_signals(name))
            continue

        articles = payload.get("articles") or []
        if not isinstance(articles, list):
            signals.extend(_fallback_signals(name))
            continue

        for article in articles:
            if not isinstance(article, dict):
                continue
            title_raw = (article.get("title") or "").strip()
            title = _clip(title_raw, 100) or f"{name} in the news"
            description = (article.get("description") or "").strip()
            published = article.get("publishedAt") or article.get("published_at") or ""
            signals.append(
                Signal(
                    source="news",
                    title=title,
                    body=_clip(description, 200),
                    impact=_impact_for_title(title_raw),
                    date=_published_date(str(published)),
                    company=name,
                    tags=_tags_from_title(title_raw),
                ),
            )

    return signals
