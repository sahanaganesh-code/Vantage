"""FastAPI entrypoint: five `/api/v1/*` routes + lightweight `/health` for probes."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router

app = FastAPI(
    title="Vantage API",
    description="Competitive intelligence API: Person 3 data layer + analyst agent.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health", tags=["ops"])
def root_health() -> dict:
    return {"status": "ok", "service": "vantage-api"}
