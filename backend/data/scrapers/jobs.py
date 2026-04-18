from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.data.models import Signal

_MOCK_PATH = Path(__file__).resolve().parent.parent / "mock" / "jobs.json"


def _load_jobs() -> list[dict[str, Any]]:
    raw = _MOCK_PATH.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, list):
        return []
    return data


def _department_impact(department: str) -> str:
    d = department.lower()
    if "ai" in d or "ml" in d or "engineering" in d:
        return "high"
    if "sales" in d or "marketing" in d:
        return "medium"
    return "low"


def _company_matches(job_company: str, query: str) -> bool:
    jc = job_company.casefold()
    q = query.casefold()
    return q in jc or jc in q


def get_job_signals(company_names: list[str]) -> list[Signal]:
    jobs = _load_jobs()
    queries = [n.strip() for n in company_names if n.strip()]
    if not queries:
        return []

    signals: list[Signal] = []
    for job in jobs:
        job_company = str(job.get("company") or "")
        if not any(_company_matches(job_company, q) for q in queries):
            continue

        role = str(job.get("role") or "open role")
        posted_date = str(job.get("posted_date") or "")
        department = str(job.get("department") or "")
        skills = job.get("skills") or []
        skill_tags = [str(s) for s in skills] if isinstance(skills, list) else []

        interpretation = str(job.get("signal_interpretation") or "").strip()
        company = job_company

        signals.append(
            Signal(
                source="job_postings",
                title=f"{company} hiring {role}",
                body=interpretation,
                impact=_department_impact(department),
                date=posted_date,
                company=company,
                tags=skill_tags,
            )
        )

    return signals
