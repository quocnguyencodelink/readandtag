# -*- coding: utf-8 -*-
import os
from pathlib import Path

# Robust .env loading from both the current working directory and default search
try:
    from dotenv import load_dotenv, find_dotenv  # pip install python-dotenv
    env_from_cwd = find_dotenv(usecwd=True)
    if env_from_cwd:
        load_dotenv(dotenv_path=env_from_cwd, override=False)
    env_default = find_dotenv()
    if env_default and env_default != env_from_cwd:
        load_dotenv(dotenv_path=env_default, override=False)
    if not (env_from_cwd or env_default):
        load_dotenv(override=False)
except Exception:
    pass  # loading .env is optional for environments using real env vars [31]

# =========================
# Box OAuth configuration
# =========================
CLIENT_ID = os.getenv("BOX_CLIENT_ID")
CLIENT_SECRET = os.getenv("BOX_CLIENT_SECRET")
REDIRECT_URI = os.getenv("BOX_REDIRECT_URI", "http://127.0.0.1:5000/callback")

TOKEN_STORE = Path.home() / ".box_tokens.json"
OUTPUT_XLSX = os.getenv("BOX_EXPORT_XLSX", "/tmp/box_export.xlsx")

# =========================
# LLM configuration (OpenAI)
# =========================
# Per-run USD budget cap
LLM_BUDGET_PER_RUN_USD = float(os.getenv("LLM_BUDGET_PER_RUN_USD", "0.125"))

# Temperature control; GPT-5 may ignore custom temperatures, but kept for legacy models
LLM_TEMPERATURE = os.getenv("LLM_TEMPERATURE", "")

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Default back to gpt-5-mini for this request
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-5-mini")  # e.g., gpt-5-mini [11]

def validate_config():
    missing = []
    if not CLIENT_ID:
        missing.append("BOX_CLIENT_ID")
    if not CLIENT_SECRET:
        missing.append("BOX_CLIENT_SECRET")
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )
