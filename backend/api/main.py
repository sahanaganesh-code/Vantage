"""FastAPI entrypoint: `/api/*` session routes + `/api/v1/*` routes used by the Vite frontend."""

from __future__ import annotations

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router, router_v1

load_dotenv()

app = FastAPI(
    title="Vantage API",
    description="Competitive intelligence: session API + v1 signals/agent.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(router_v1)


@app.get("/health", tags=["ops"])
def root_health() -> dict[str, str]:
    return {"status": "ok", "service": "vantage-api"}
