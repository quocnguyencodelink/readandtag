# -*- coding: utf-8 -*-
import os
from pathlib import Path

# Load environment variables from a local .env if present.
# This supports easy local development while still allowing real env vars to be used in other environments.
try:
    from dotenv import load_dotenv  # pip install python-dotenv
    load_dotenv()  # does not override existing environment variables by default
except Exception:
    # If python-dotenv isn't installed, env vars can still be provided by the OS environment.
    pass

# IMPORTANT: Values are read from environment variables (optionally supplied by .env during development).
# Do not hard-code secrets here.

CLIENT_ID = os.getenv("BOX_CLIENT_ID")
CLIENT_SECRET = os.getenv("BOX_CLIENT_SECRET")
# Redirect URI can safely keep a development default; must match the Box app settings exactly.
REDIRECT_URI = os.getenv("BOX_REDIRECT_URI", "http://127.0.0.1:5000/callback")

# Token storage (simple JSON file in the user's home)
TOKEN_STORE = Path.home() / ".box_tokens.json"

# Default export path (the app now prompts for Save As; this remains a fallback/default)
OUTPUT_XLSX = os.getenv("BOX_EXPORT_XLSX", "/tmp/box_export.xlsx")

def validate_config():
    """
    Simple validation to help catch missing required configuration early.
    Call this from startup if you want strict checks before running OAuth/UI.
    """
    missing = []
    if not CLIENT_ID:
        missing.append("BOX_CLIENT_ID")
    if not CLIENT_SECRET:
        missing.append("BOX_CLIENT_SECRET")
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Create a .env from .env.example (or .env) and set these values, "
            "or export them in the environment before running the app."
        )
