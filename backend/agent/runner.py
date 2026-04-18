"""Analyst agent: builds prompts from Person 3 data + `get_job_signals`, calls OpenAI when configured."""

from __future__ import annotations

import json
import os
from typing import Any, Optional

from backend.agent.prompts import SYSTEM_ANALYST, format_user_prompt
from backend.data.processors.signal_processor import get_signals_for_company
from backend.data.scrapers.jobs import get_job_signals


def _dump_signals(signals: list[Any]) -> str:
    payload = [s.model_dump() if hasattr(s, "model_dump") else s for s in signals]
    return json.dumps(payload, indent=2)[:24_000]


def build_agent_context(company_name: str, competitors: list[str]) -> tuple[str, str, int, int]:
    """
    Pull ranked signals from the Person 3 processor and job-only slice from jobs scraper
    (jobs are also inside the processor output; we still surface a dedicated jobs block for the model).
    """
    job_signals = get_job_signals(competitors)
    all_signals = get_signals_for_company(company_name, competitors)
    jobs_block = _dump_signals(job_signals)
    signals_block = _dump_signals(all_signals)
    return jobs_block, signals_block, len(all_signals), len(job_signals)


def run_competitive_analysis(
    company_name: str,
    competitors: list[str],
    user_query: Optional[str] = None,
) -> dict[str, Any]:
    jobs_block, signals_block, n_signals, n_jobs = build_agent_context(company_name, competitors)
    user_prompt = format_user_prompt(
        company_name=company_name,
        competitors=competitors,
        jobs_json=jobs_block,
        signals_json=signals_block,
        user_query=user_query or "",
    )

    key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not key:
        return {
            "mock": True,
            "analysis": (
                "OpenAI is not configured (missing OPENAI_API_KEY). "
                f"Loaded {n_signals} ranked signals and {n_jobs} job signals for prompt context."
            ),
            "model": None,
            "signals_used": n_signals,
            "job_signals_used": n_jobs,
        }

    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - guarded by requirements
        raise RuntimeError("openai package is required for live agent calls") from exc

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI()
    completion = client.chat.completions.create(
        model=model,
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_ANALYST},
            {"role": "user", "content": user_prompt},
        ],
    )
    text = (completion.choices[0].message.content or "").strip()
    return {
        "mock": False,
        "analysis": text,
        "model": model,
        "signals_used": n_signals,
        "job_signals_used": n_jobs,
    }
