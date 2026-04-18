"""Static JSON stubs for API routes when USE_API_STUBS=1 (frontend / offline demos)."""

MOCK_SIGNALS_RESPONSE: dict = {
    "stub": True,
    "company_name": "DemoCo",
    "competitors": ["Notion", "Linear"],
    "signals": [
        {
            "source": "news",
            "title": "Notion announces enterprise AI assistant (stub)",
            "body": "Placeholder body for stubbed news signal.",
            "impact": "high",
            "date": "2025-03-01",
            "company": "Notion",
            "tags": ["ai", "enterprise"],
        }
    ],
}

MOCK_JOBS_RESPONSE: dict = {
    "stub": True,
    "competitors": ["Notion"],
    "jobs": [
        {
            "source": "job_postings",
            "title": "Notion hiring Senior ML Engineer (stub)",
            "body": "Stub interpretation of hiring intent.",
            "impact": "high",
            "date": "2025-03-10",
            "company": "Notion",
            "tags": ["Python", "LLMs"],
        }
    ],
}

MOCK_NEWS_RESPONSE: dict = {
    "stub": True,
    "competitors": ["Linear"],
    "news": [
        {
            "source": "news",
            "title": "Linear rolls out workflow automation updates (stub)",
            "body": "Stub coverage for offline mode.",
            "impact": "medium",
            "date": "2025-02-15",
            "company": "Linear",
            "tags": ["product", "saas"],
        }
    ],
}

MOCK_FUNDING_RESPONSE: dict = {
    "stub": True,
    "competitors": ["Ramp"],
    "funding": [
        {
            "source": "funding",
            "title": "Ramp raises $300M Series D (stub)",
            "body": "Stub funding interpretation.",
            "impact": "high",
            "date": "2025-03-03",
            "company": "Ramp",
            "tags": ["funding", "Series D", "growth"],
        }
    ],
}

MOCK_AGENT_RESPONSE: dict = {
    "stub": True,
    "mock": True,
    "analysis": (
        "Stub analyst output: competitors show steady AI hiring and funding activity. "
        "Validate with live signals by disabling USE_API_STUBS and setting OPENAI_API_KEY."
    ),
    "model": None,
    "signals_used": 1,
    "job_signals_used": 1,
}
