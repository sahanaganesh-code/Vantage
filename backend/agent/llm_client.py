import os

from google import genai as google_genai
from google.genai import types as genai_types
from openai import OpenAI


def _ollama_base_url() -> str:
    host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
    if host.endswith("/v1"):
        return host
    return f"{host}/v1"


def _call_ollama(prompt: str) -> str:
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    return _call_openai_chat(
        prompt=prompt,
        model=model,
        base_url=_ollama_base_url(),
        api_key="ollama",
        label="Ollama",
    )


def _call_gemini(prompt: str, api_key: str) -> str:
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    try:
        client = google_genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=genai_types.GenerateContentConfig(max_output_tokens=1500),
        )
        text = getattr(response, "text", None)
        if text:
            return text
        parts: list[str] = []
        if response.candidates:
            for c in response.candidates:
                content = getattr(c, "content", None)
                if not content:
                    continue
                for p in getattr(content, "parts", []) or []:
                    t = getattr(p, "text", None)
                    if t:
                        parts.append(t)
        if parts:
            return "".join(parts)
        return "error: empty response from Gemini"
    except Exception as exc:  # noqa: BLE001
        return f"error: {exc}"


def _call_openai_chat(
    *,
    prompt: str,
    model: str,
    base_url: str | None,
    api_key: str | None,
    label: str,
) -> str:
    kwargs: dict = {}
    if base_url:
        kwargs["base_url"] = base_url
    if api_key:
        kwargs["api_key"] = api_key
    client = OpenAI(**kwargs)
    response = client.chat.completions.create(
        model=model,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content
    if content is None:
        return f"error: empty response from {label}"
    return content


def _is_groq_style_key(value: str) -> bool:
    """Groq-issued keys almost always start with gsk_. Those must go to api.groq.com, not api.x.ai."""
    return value.strip().lower().startswith("gsk_")


def _groq_api_key() -> str | None:
    """
    Groq (Llama, etc.): key from https://console.groq.com/keys — typically starts with gsk_.
    Reads GROQ_API_KEY first; if missing, accepts a gsk_ value mistakenly stored in GROK_/XAI_ vars.
    """
    direct = (os.getenv("GROQ_API_KEY") or "").strip()
    if direct:
        return direct
    for env_name in ("GROK_API_KEY", "XAI_API_KEY"):
        v = (os.getenv(env_name) or "").strip()
        if v and _is_groq_style_key(v):
            return v
    return None


def _grok_api_key() -> str | None:
    """
    Grok (xAI chat): key from https://console.x.ai/ — must NOT be a Groq gsk_ key.
    """
    for env_name in ("GROK_API_KEY", "XAI_API_KEY"):
        v = (os.getenv(env_name) or "").strip()
        if v and not _is_groq_style_key(v):
            return v
    return None


def _grok_misconfigured_groq_key_message() -> str:
    return (
        "error: LLM key mix-up (this is why xAI said 'Incorrect API key'):\n\n"
        "• Keys starting with gsk_ come from GROQ (Groq): https://console.groq.com/keys\n"
        "  Use: VANTAGE_LLM=groq and GROQ_API_KEY=gsk_...\n\n"
        "• Grok (different company, xAI) uses a different key from: https://console.x.ai/\n"
        "  Use: VANTAGE_LLM=grok and GROK_API_KEY=<key from console.x.ai> (not gsk_)\n\n"
        "You currently have a gsk_ key but VANTAGE_LLM=grok (or Grok vars). "
        "Switch to VANTAGE_LLM=groq and move the key to GROQ_API_KEY, or get a real Grok key from console.x.ai."
    )


def _grok_model() -> str:
    return os.getenv("GROK_MODEL") or os.getenv("XAI_MODEL", "grok-3-mini")


def _call_grok(prompt: str, api_key: str) -> str:
    """Grok is served at api.x.ai (OpenAI-compatible); there is no separate non-xAI Grok host."""
    model = _grok_model()
    return _call_openai_chat(
        prompt=prompt,
        model=model,
        base_url="https://api.x.ai/v1",
        api_key=api_key,
        label="Grok",
    )


def call_llm(prompt: str) -> str:
    """
    Providers:
    - VANTAGE_LLM=ollama — local Ollama (no API key)
    - VANTAGE_LLM=gemini|groq|grok|openai — cloud (needs matching key)
    - Auto: GEMINI → GROQ → GROK → OPENAI; if none, try Ollama
    """
    forced = os.getenv("VANTAGE_LLM", "").lower().strip()
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = _groq_api_key()
    grok_key = _grok_api_key()
    openai_key = os.getenv("OPENAI_API_KEY")

    try:
        if forced == "ollama":
            return _call_ollama(prompt)
        if forced in ("gemini", "google"):
            if not gemini_key:
                return "error: VANTAGE_LLM=gemini but GEMINI_API_KEY is not set"
            return _call_gemini(prompt, gemini_key)
        if forced == "groq":
            if not groq_key:
                return (
                    "error: VANTAGE_LLM=groq but no Groq key found. "
                    "Create one at https://console.groq.com/keys and set GROQ_API_KEY=gsk_... "
                    "(a gsk_ key in GROK_API_KEY / XAI_API_KEY is also accepted.)"
                )
            model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
            return _call_openai_chat(
                prompt=prompt,
                model=model,
                base_url="https://api.groq.com/openai/v1",
                api_key=groq_key,
                label="Groq",
            )
        if forced in ("grok", "xai"):
            if grok_key:
                return _call_grok(prompt, grok_key)
            misplaced = (os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY") or "").strip()
            if misplaced and _is_groq_style_key(misplaced):
                return _grok_misconfigured_groq_key_message()
            return (
                "error: VANTAGE_LLM=grok but no valid Grok (xAI) key found. "
                "Create a key at https://console.x.ai/ and set GROK_API_KEY or XAI_API_KEY "
                "(do not use a Groq gsk_ key there)."
            )
        if forced == "openai":
            if not openai_key:
                return "error: VANTAGE_LLM=openai but OPENAI_API_KEY is not set"
            model = os.getenv("OPENAI_MODEL", "gpt-4o")
            return _call_openai_chat(
                prompt=prompt,
                model=model,
                base_url=None,
                api_key=None,
                label="OpenAI",
            )
        if forced:
            return (
                f"error: unknown VANTAGE_LLM={forced!r} "
                "(use ollama, gemini, groq, grok, or openai)"
            )

        if gemini_key:
            return _call_gemini(prompt, gemini_key)
        if groq_key:
            model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
            return _call_openai_chat(
                prompt=prompt,
                model=model,
                base_url="https://api.groq.com/openai/v1",
                api_key=groq_key,
                label="Groq",
            )
        if grok_key:
            return _call_grok(prompt, grok_key)
        if openai_key:
            model = os.getenv("OPENAI_MODEL", "gpt-4o")
            return _call_openai_chat(
                prompt=prompt,
                model=model,
                base_url=None,
                api_key=None,
                label="OpenAI",
            )

        return _call_ollama(prompt)
    except Exception as exc:  # noqa: BLE001
        if not any([gemini_key, groq_key, grok_key, openai_key]) and not forced:
            return (
                "error: no cloud LLM keys set, and Ollama is not reachable "
                f"({exc}). Install https://ollama.com, run `ollama pull llama3.2`, "
                "start the Ollama app (or `ollama serve`), then retry. "
                "Or set VANTAGE_LLM=ollama after fixing Ollama. "
                "Cloud: GEMINI_API_KEY / GROQ_API_KEY / GROK_API_KEY / OPENAI_API_KEY."
            )
        return f"error: {exc}"
