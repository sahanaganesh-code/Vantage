"""Integration surface for the rest of the backend: map `Company` → ranked `Signal` payloads."""

from __future__ import annotations

from backend.data.models import Company, Signal
from backend.data.processors.signal_processor import get_signals_for_company


def get_signals_for_company_model(company: Company) -> list[Signal]:
    """Return live ranked signals for the company's competitive set."""
    return get_signals_for_company(company.name, company.competitors)


def get_signals_for_company_payload(company: Company) -> list[dict]:
    """JSON-serializable signals for APIs, queues, or agents."""
    return [s.model_dump() for s in get_signals_for_company_model(company)]
