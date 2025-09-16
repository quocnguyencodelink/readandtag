# -*- coding: utf-8 -*-
import os
from pathlib import Path

# IMPORTANT: Set these to match the Box app configuration
CLIENT_ID = os.getenv("BOX_CLIENT_ID", "vi6jvs5px2441b00zxh3i84taddj3epp")
CLIENT_SECRET = os.getenv("BOX_CLIENT_SECRET", "QPqj4mvGMLGmJD4hfd2XwPsxGFAArF06")
REDIRECT_URI = os.getenv("BOX_REDIRECT_URI", "http://127.0.0.1:5000/callback")  # Must match Box app settings

# Token storage (simple JSON file in the user's home)
TOKEN_STORE = Path.home() / ".box_tokens.json"

# Output Excel path
OUTPUT_XLSX = os.getenv("BOX_EXPORT_XLSX", "/tmp/box_export.xlsx")
