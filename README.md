# readandtag

Authenticates with Box, lets a user pick a folder via Tkinter, recursively finds video files, and exports results to Excel. [Instructions below.]

## Requirements
- Python 3.12
- macOS
- Dependencies: boxsdk, flask, pandas

## Install
python3 -m venv .venv
source .venv/bin/activate
pip install boxsdk flask pandas


## Configure OAuth
Set these environment variables (copy from .env.example to a local `.env`, but do not commit it):
- BOX_CLIENT_ID
- BOX_CLIENT_SECRET
- BOX_REDIRECT_URI (e.g., http://127.0.0.1:5000/callback)

Ensure the Redirect URI exactly matches one configured in the Box Developer Console. 

## Run
python3 main.py

- Browser opens for Box OAuth on first run. 
- Tkinter shows a folder picker; after selection, a Save As dialog prompts for the Excel destination. 
- The Excel contains one row per discovered video file.

