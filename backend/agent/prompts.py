"""Prompt templates for the competitive intelligence analyst (LLM-agnostic strings)."""

from __future__ import annotations

SYSTEM_ANALYST = """You are Vantage, a B2B competitive intelligence analyst.
You receive normalized signals (news, job postings, funding). Be precise, cite companies by name,
and separate facts stated in the signals from your inferences. Keep answers concise unless asked for detail."""

USER_ANALYSIS_TEMPLATE = """## Context
- Client company (for positioning only): {company_name}
- Competitors monitored: {competitors_csv}

## Job posting signals (prioritize these for workforce and roadmap intent)
{jobs_json}

## Full competitive signal set (news, jobs, funding — deduped and ranked upstream)
{signals_json}

## User request
{user_query}
"""


def format_user_prompt(
    *,
    company_name: str,
    competitors: list[str],
    jobs_json: str,
    signals_json: str,
    user_query: str,
) -> str:
    return USER_ANALYSIS_TEMPLATE.format(
        company_name=company_name or "(not specified)",
        competitors_csv=", ".join(competitors) if competitors else "(none)",
        jobs_json=jobs_json,
        signals_json=signals_json,
        user_query=user_query.strip() if user_query.strip() else "Summarize the strongest competitive moves and risks.",
    )
