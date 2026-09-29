from __future__ import annotations

import os

from dotenv import load_dotenv


load_dotenv(".env")


def get_agent_mode() -> str:
    mode = os.getenv("AGENT_MODE", "local").strip().lower()

    if mode not in {"local", "openai"}:
        raise ValueError(
            "AGENT_MODE must be either 'local' or 'openai'"
        )

    return mode


def get_openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-5.6")


def has_openai_key() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))
