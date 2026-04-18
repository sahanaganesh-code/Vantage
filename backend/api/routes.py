from __future__ import annotations

import os
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from backend.agent.runner import run_competitive_analysis
from backend.api.mocks import (
    MOCK_AGENT_RESPONSE,
    MOCK_FUNDING_RESPONSE,
    MOCK_JOBS_RESPONSE,
    MOCK_NEWS_RESPONSE,
    MOCK_SIGNALS_RESPONSE,
)
from backend.data.processors.signal_processor import get_signals_for_company
from backend.data.scrapers.funding import get_funding_signals
from backend.data.scrapers.jobs import get_job_signals
from backend.data.scrapers.news import get_news_signals

router = APIRouter(prefix="/api/v1", tags=["vantage"])


def _use_stubs() -> bool:
    return os.getenv("USE_API_STUBS", "").strip() == "1"


def _parse_competitors(competitors: Optional[str]) -> list[str]:
    if not competitors:
        return []
    return [part.strip() for part in competitors.split(",") if part.strip()]


@router.get("/signals")
def get_signals(
    company_name: str = Query(default="", description="Client company name (optional)"),
    competitors: Optional[str] = Query(
        default=None,
        description="Comma-separated competitor names to monitor",
    ),
):
    """Ranked competitive signals from Person 3 processor (news + jobs + funding)."""
    if _use_stubs():
        return MOCK_SIGNALS_RESPONSE
    comp = _parse_competitors(competitors)
    signals = get_signals_for_company(company_name, comp)
    return {
        "stub": False,
        "company_name": company_name,
        "competitors": comp,
        "signals": [s.model_dump() for s in signals],
    }


@router.get("/jobs")
def get_jobs(
    competitors: Optional[str] = Query(
        default=None,
        description="Comma-separated competitor names",
    ),
):
    """Job posting signals only (`get_job_signals`), also fed prominently to the analyst agent."""
    if _use_stubs():
        return MOCK_JOBS_RESPONSE
    comp = _parse_competitors(competitors)
    jobs = get_job_signals(comp)
    return {
        "stub": False,
        "competitors": comp,
        "jobs": [s.model_dump() for s in jobs],
    }


@router.get("/news")
def get_news(
    competitors: Optional[str] = Query(
        default=None,
        description="Comma-separated competitor names",
    ),
):
    """News signals only (`get_news_signals`)."""
    if _use_stubs():
        return MOCK_NEWS_RESPONSE
    comp = _parse_competitors(competitors)
    news = get_news_signals(comp)
    return {
        "stub": False,
        "competitors": comp,
        "news": [s.model_dump() for s in news],
    }


@router.get("/funding")
def get_funding(
    competitors: Optional[str] = Query(
        default=None,
        description="Comma-separated competitor names",
    ),
):
    """Funding signals only (`get_funding_signals`)."""
    if _use_stubs():
        return MOCK_FUNDING_RESPONSE
    comp = _parse_competitors(competitors)
    funding = get_funding_signals(comp)
    return {
        "stub": False,
        "competitors": comp,
        "funding": [s.model_dump() for s in funding],
    }


class AgentAnalyzeRequest(BaseModel):
    company_name: str = ""
    competitors: list[str] = Field(default_factory=list)
    query: Optional[str] = None


@router.post("/agent/analyze")
def post_agent_analyze(body: AgentAnalyzeRequest):
    """
    Analyst agent: prompt templates + Person 3 signals, with **job signals** highlighted in the prompt.
    Set `OPENAI_API_KEY` for live OpenAI; otherwise returns a deterministic fallback payload.
    """
    if _use_stubs():
        return MOCK_AGENT_RESPONSE
    return run_competitive_analysis(body.company_name, body.competitors, body.query)
