from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from backend.agent import workflows
from backend.api.models import (
    Action,
    BattlecardRequest,
    BattlecardResponse,
    BriefRequest,
    BriefResponse,
    PrioritizeRequest,
    PrioritizeResponse,
    RankedAccount,
    SetupRequest,
    SetupResponse,
    Signal,
    SignalsResponse,
)
from backend.data.processors.signal_processor import get_signals_for_company

router = APIRouter(prefix="/api", tags=["vantage"])

sessions: dict[str, dict[str, Any]] = {}


def _get_session(session_id: str) -> dict[str, Any]:
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    return session


def _coerce_signals(raw: Any) -> list[Signal]:
    if not isinstance(raw, list):
        return []
    out: list[Signal] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            out.append(Signal.model_validate(item))
        except Exception:
            continue
    return out


def _normalize_action_dict(item: dict[str, Any]) -> dict[str, Any] | None:
    """Map common LLM shapes onto Action { text, urgency }."""
    text = (
        item.get("text")
        or item.get("description")
        or item.get("action")
        or item.get("recommendation")
        or item.get("title")
    )
    if not isinstance(text, str) or not text.strip():
        return None
    raw_u = item.get("urgency") or item.get("timeline") or item.get("priority")
    u = str(raw_u).strip().lower().replace(" ", "-").replace("_", "-") if raw_u is not None else ""
    if u in ("this-week", "thisweek", "week", "high", "immediate", "urgent", "p0", "p1"):
        urgency: str = "this-week"
    elif u in ("this-month", "thismonth", "month", "medium", "low", "p2", "p3", "soon"):
        urgency = "this-month"
    else:
        urgency = "this-month"
    return {"text": text.strip(), "urgency": urgency}


def _coerce_actions(raw: Any) -> list[Action]:
    if not isinstance(raw, list):
        return []
    out: list[Action] = []
    for item in raw:
        if isinstance(item, str):
            candidate = {"text": item.strip(), "urgency": "this-month"}
        elif isinstance(item, dict):
            norm = _normalize_action_dict(item)
            candidate = norm if norm else item
        else:
            continue
        try:
            out.append(Action.model_validate(candidate))
        except Exception:
            continue
    return out


def _coerce_ranked_accounts(raw: Any) -> list[RankedAccount]:
    if not isinstance(raw, list):
        return []
    out: list[RankedAccount] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            sigs = _coerce_signals(item.get("signals", []))
            score = item.get("score", 0)
            if isinstance(score, float):
                score = int(round(score))
            elif isinstance(score, str) and score.isdigit():
                score = int(score)
            elif not isinstance(score, int):
                score = 0
            payload = {
                **item,
                "score": max(0, min(100, score)),
                "signals": [s.model_dump() for s in sigs],
            }
            out.append(RankedAccount.model_validate(payload))
        except Exception:
            continue
    return out


@router.post("/setup", response_model=SetupResponse)
def setup(body: SetupRequest) -> SetupResponse:
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "company": body.company,
        "competitors": body.competitors,
        "accounts": body.accounts,
        "signals": [],
    }
    return SetupResponse(session_id=session_id)


@router.post("/brief", response_model=BriefResponse)
def brief(body: BriefRequest) -> BriefResponse:
    session = _get_session(body.session_id)
    company = session["company"]
    signals_raw: list[dict[str, Any]] = session.get("signals") or []
    result = workflows.generate_brief(company, body.competitor, signals_raw)
    sigs = _coerce_signals(result.get("signals"))
    actions = _coerce_actions(result.get("actions"))
    summary = result.get("summary") if isinstance(result.get("summary"), str) else ""
    if not summary and isinstance(result.get("error"), str):
        summary = result["error"]
    return BriefResponse(signals=sigs, summary=summary or "", actions=actions)


@router.post("/prioritize", response_model=PrioritizeResponse)
def prioritize(body: PrioritizeRequest) -> PrioritizeResponse:
    session = _get_session(body.session_id)
    company = session["company"]
    accounts: list[str] = session.get("accounts") or []
    signals_raw: list[dict[str, Any]] = session.get("signals") or []
    result = workflows.prioritize_accounts(company, accounts, signals_raw)
    accounts_out = _coerce_ranked_accounts(result.get("accounts"))
    return PrioritizeResponse(accounts=accounts_out)


@router.post("/battlecard", response_model=BattlecardResponse)
def battlecard(body: BattlecardRequest) -> BattlecardResponse:
    session = _get_session(body.session_id)
    company = session["company"]
    signals_raw: list[dict[str, Any]] = session.get("signals") or []
    result = workflows.generate_battlecard(company, body.competitor, signals_raw)
    md = result.get("markdown") if isinstance(result.get("markdown"), str) else ""
    if not md and isinstance(result.get("error"), str):
        md = result["error"]
    return BattlecardResponse(markdown=md or "")


@router.get("/signals", response_model=SignalsResponse)
def signals(session_id: str = Query(..., alias="session_id")) -> SignalsResponse:
    session = _get_session(session_id)
    company = session["company"]
    rows = get_signals_for_company(company)
    session["signals"] = rows
    sigs = _coerce_signals(rows)
    return SignalsResponse(signals=sigs)
