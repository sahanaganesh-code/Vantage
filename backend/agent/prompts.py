"""Prompt templates: hackathon brief/prioritize/battlecard + v1 analyst agent."""

from __future__ import annotations

# --- Person 2 workflows (POST /api/brief, prioritize, battlecard) ---
BRIEF_PROMPT = """Given company={company}, competitor={competitor}, and these market signals: {signals_json}, produce a JSON object with:
- summary: 2-3 sentence strategic summary of competitor threat level
- signals: the top 5 most impactful signals (reuse input format)
- actions: 3 specific actions the sales/product team should take this week or month
Always return valid JSON only, no markdown."""

PRIORITIZE_PROMPT = """Given company={company} trying to close accounts={accounts_json}, and these signals={signals_json}, rank each account by buying likelihood this quarter. Return JSON array of {{ name, score (0-100), reason (1 sentence), signals (top 2 relevant signals) }}. JSON only."""

BATTLECARD_PROMPT = """Given company={company} competing against {competitor} with these signals={signals_json}, write a sales battle card in markdown. Sections: Overview (2 sentences), Their Strengths (3 bullets), Their Weaknesses (3 bullets, from review/signal data), Our Angle (how to position against them), Objection Handlers (2 common objections + responses). Be specific and actionable."""

# --- Person 3 / v1 analyst (`runner.py`) ---
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
