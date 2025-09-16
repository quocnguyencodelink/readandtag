# -*- coding: utf-8 -*-
import json
import threading
import webbrowser
from flask import Flask, request
from boxsdk import OAuth2, Client

from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, TOKEN_STORE

app = Flask(__name__)
_auth_ready_event = threading.Event()
_auth_error = None
_oauth_obj = None  # set in get_box_client()

def _store_tokens(access_token, refresh_token):
    """Callback used by the Box SDK to persist refreshed tokens."""
    data = {"access_token": access_token, "refresh_token": refresh_token}
    TOKEN_STORE.write_text(json.dumps(data))

def _load_tokens():
    """Load tokens from local store if present."""
    if TOKEN_STORE.exists():
        data = json.loads(TOKEN_STORE.read_text())
        return data.get("access_token"), data.get("refresh_token")
    return None, None

@app.route("/callback")
def oauth_callback():
    """Handle the OAuth2 redirect with the authorization code."""
    global _auth_error, _oauth_obj
    try:
        code = request.args.get("code")
        if not code:
            _auth_error = "No authorization code returned"
            _auth_ready_event.set()
            return "Authorization failed. No code received.", 400

        # Exchange code for tokens; store_tokens will be called by SDK
        _oauth_obj.authenticate(code)
        _auth_ready_event.set()
        return "Authorization complete. This window can be closed."
    except Exception as e:
        _auth_error = str(e)
        _auth_ready_event.set()
        return f"Authorization error: {e}", 500

def _run_flask():
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

def get_box_client() -> Client:
    """
    Returns an authenticated Box Client, performing OAuth2 on first run.
    Reuses and refreshes tokens on subsequent runs.
    """
    global _oauth_obj
    access_token, refresh_token = _load_tokens()

    _oauth_obj = OAuth2(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        store_tokens=_store_tokens,
        access_token=access_token,
        refresh_token=refresh_token,
    )

    # If tokens exist, return client (SDK will auto-refresh when needed)
    if access_token and refresh_token:
        return Client(_oauth_obj)

    # Otherwise start local callback server and run the auth flow
    _auth_ready_event.clear()
    flask_thread = threading.Thread(target=_run_flask, daemon=True)
    flask_thread.start()

    # Create authorization URL and open browser
    auth_url, _csrf = _oauth_obj.get_authorization_url(REDIRECT_URI)
    webbrowser.open(auth_url)

    # Wait for callback
    _auth_ready_event.wait(timeout=300)
    if _auth_error:
        raise RuntimeError(f"OAuth error: {_auth_error}")

    return Client(_oauth_obj)
