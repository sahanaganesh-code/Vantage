import json
import re
from typing import Any

from backend.agent.llm_client import call_llm
from backend.agent.prompts import BATTLECARD_PROMPT, BRIEF_PROMPT, PRIORITIZE_PROMPT


def _signals_to_json(signals: list[dict[str, Any]]) -> str:
    return json.dumps(signals, ensure_ascii=False)


def _extract_json_text(raw: str) -> str:
    text = raw.strip()
    fence = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", text, re.DOTALL | re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    return text


def generate_brief(company: str, competitor: str, signals: list[dict[str, Any]]) -> dict[str, Any]:
    prompt = BRIEF_PROMPT.format(
        company=company,
        competitor=competitor,
        signals_json=_signals_to_json(signals),
    )
    raw = call_llm(prompt)
    if raw.startswith("error:"):
        return {
            "summary": raw,
            "signals": [],
            "actions": [],
            "error": raw,
        }
    try:
        return json.loads(_extract_json_text(raw))
    except json.JSONDecodeError as exc:
        return {
            "summary": "Could not parse LLM response as JSON.",
            "signals": [],
            "actions": [],
            "error": f"json parse failed: {exc}",
        }


def prioritize_accounts(
    company: str,
    accounts: list[str],
    signals: list[dict[str, Any]],
) -> dict[str, Any]:
    prompt = PRIORITIZE_PROMPT.format(
        company=company,
        accounts_json=json.dumps(accounts, ensure_ascii=False),
        signals_json=_signals_to_json(signals),
    )
    raw = call_llm(prompt)
    if raw.startswith("error:"):
        return {"accounts": [], "error": raw}
    try:
        parsed = json.loads(_extract_json_text(raw))
        if isinstance(parsed, list):
            return {"accounts": parsed}
        if isinstance(parsed, dict) and "accounts" in parsed:
            return parsed
        return {"accounts": [], "error": "unexpected JSON shape from LLM"}
    except json.JSONDecodeError as exc:
        return {"accounts": [], "error": f"json parse failed: {exc}"}


def generate_battlecard(
    company: str,
    competitor: str,
    signals: list[dict[str, Any]],
) -> dict[str, Any]:
    prompt = BATTLECARD_PROMPT.format(
        company=company,
        competitor=competitor,
        signals_json=_signals_to_json(signals),
    )
    raw = call_llm(prompt)
    if raw.startswith("error:"):
        return {"markdown": raw, "error": raw}
    text = raw.strip()
    fence = re.match(r"^```(?:markdown|md)?\s*\n?(.*?)\n?```\s*$", text, re.DOTALL | re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    return {"markdown": text}
