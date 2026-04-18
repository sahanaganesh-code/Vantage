"""FastAPI entrypoint: five `/api/v1/*` routes + lightweight `/health` for probes."""

from __future__ import annotations

from fastapi import FastAPI

from backend.api.routes import router

app = FastAPI(
    title="Vantage API",
    description="Competitive intelligence API: Person 3 data layer + analyst agent.",
    version="0.1.0",
)

app.include_router(router)


@app.get("/health", tags=["ops"])
def root_health() -> dict:
    return {"status": "ok", "service": "vantage-api"}
