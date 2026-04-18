from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from backend.data.models import Signal

_MOCK_PATH = Path(__file__).resolve().parent.parent / "mock" / "funding.json"


def _load_funding() -> list[dict[str, Any]]:
    raw = _MOCK_PATH.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, list):
        return []
    return data


_AMOUNT_RE = re.compile(r"\$\s*([\d,.]+)\s*([KMB])?", re.IGNORECASE)


def _amount_usd(amount: str) -> float | None:
    m = _AMOUNT_RE.search(amount or "")
    if not m:
        return None
    num_raw = m.group(1).replace(",", "")
    try:
        num = float(num_raw)
    except ValueError:
        return None
    suffix = (m.group(2) or "").upper()
    mult = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}.get(suffix, 1.0)
    return num * mult


def _funding_impact(amount: str) -> str:
    dollars = _amount_usd(amount)
    if dollars is None:
        return "medium"
    return "high" if dollars >= 50_000_000 else "medium"


def _company_matches(event_company: str, query: str) -> bool:
    ec = event_company.casefold()
    q = query.casefold()
    return q in ec or ec in q


def get_funding_signals(company_names: list[str]) -> list[Signal]:
    rows = _load_funding()
    queries = [n.strip() for n in company_names if n.strip()]
    if not queries:
        return []

    signals: list[Signal] = []
    for row in rows:
        company = str(row.get("company") or "")
        if not any(_company_matches(company, q) for q in queries):
            continue

        amount = str(row.get("amount") or "")
        funding_round = str(row.get("round") or "")
        event_date = str(row.get("date") or "")
        interpretation = str(row.get("signal_interpretation") or "").strip()

        signals.append(
            Signal(
                source="funding",
                title=f"{company} raises {amount} {funding_round}".strip(),
                body=interpretation,
                impact=_funding_impact(amount),
                date=event_date,
                company=company,
                tags=["funding", funding_round, "growth"],
            )
        )

    return signals
