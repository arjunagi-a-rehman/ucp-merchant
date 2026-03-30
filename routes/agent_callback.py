"""
Agent OAuth Callback — handles the redirect after user signs in.
Exchanges the Firebase ID token for a UCP JWT, stores it in Firestore
so the ADK agent can pick it up by session_id.
"""
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from datetime import timedelta
from security import create_access_token

FIREBASE_API_KEY = "AIzaSyCCIpMYY-y1weaHjCgmg1ThljFpImjtzrE"
FIRESTORE_PROJECT = "ucp-demo-1f0cf"
FIRESTORE_BASE = f"https://firestore.googleapis.com/v1/projects/{FIRESTORE_PROJECT}/databases/(default)/documents"

router = APIRouter(prefix="/agent", tags=["agent"])


def _firestore_write(collection: str, doc_id: str, fields: dict):
    """Write a doc to Firestore using the REST API (no auth needed for public rules)."""
    # For demo: Firestore in test mode allows public writes.
    # In production, use a service account token.
    url = f"{FIRESTORE_BASE}/{collection}/{doc_id}"
    body = {"fields": {}}
    for k, v in fields.items():
        if isinstance(v, str):
            body["fields"][k] = {"stringValue": v}
        elif isinstance(v, (int, float)):
            body["fields"][k] = {"doubleValue": v}
        elif isinstance(v, bool):
            body["fields"][k] = {"booleanValue": v}

    resp = httpx.patch(url, json=body, timeout=10)
    if not resp.is_success:
        raise Exception(f"Firestore write failed: {resp.text}")


def _firestore_read(collection: str, doc_id: str) -> dict | None:
    """Read a doc from Firestore using the REST API."""
    url = f"{FIRESTORE_BASE}/{collection}/{doc_id}"
    resp = httpx.get(url, timeout=10)
    if resp.status_code == 404:
        return None
    if not resp.is_success:
        return None

    data = resp.json()
    fields = data.get("fields", {})
    result = {}
    for k, v in fields.items():
        if "stringValue" in v:
            result[k] = v["stringValue"]
        elif "doubleValue" in v:
            result[k] = v["doubleValue"]
        elif "booleanValue" in v:
            result[k] = v["booleanValue"]
        elif "integerValue" in v:
            result[k] = int(v["integerValue"])
    return result


@router.get("/callback", response_class=HTMLResponse)
def agent_oauth_callback(code: str = None, session_id: str = None, state: str = None):
    """
    OAuth callback for AI agents.
    - Receives the Firebase ID token as `code`
    - Exchanges it for a UCP JWT
    - Stores the JWT in Firestore keyed by session_id
    - Shows a success page to the user
    """
    # Use state as session_id fallback
    sid = session_id or state
    if not code or not sid:
        return HTMLResponse(
            content=_error_page("Missing code or session_id"),
            status_code=400,
        )

    # Verify Firebase ID token
    try:
        resp = httpx.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}",
            json={"idToken": code},
            timeout=10,
        )
        if resp.status_code != 200:
            return HTMLResponse(content=_error_page("Invalid or expired sign-in token"), status_code=401)

        users = resp.json().get("users", [])
        if not users:
            return HTMLResponse(content=_error_page("Could not identify user"), status_code=401)

        user = users[0]
        uid = user.get("localId")
        email = user.get("email", "")
    except Exception as e:
        return HTMLResponse(content=_error_page(f"Auth error: {e}"), status_code=500)

    # Generate UCP JWT
    access_token = create_access_token(
        data={"sub": uid, "client_id": "adk_agent", "email": email},
        expires_delta=timedelta(hours=1),
    )

    # Store in Firestore
    try:
        _firestore_write("agent_sessions", sid, {
            "token": access_token,
            "uid": uid,
            "email": email,
            "status": "linked",
        })
    except Exception as e:
        return HTMLResponse(content=_error_page(f"Failed to save session: {e}"), status_code=500)

    return HTMLResponse(content=_success_page(email))


@router.get("/session/{session_id}")
def get_agent_session(session_id: str):
    """
    Poll endpoint for the ADK agent to check if the user has completed sign-in.
    Returns the auth token if available.
    """
    data = _firestore_read("agent_sessions", session_id)
    if not data or data.get("status") != "linked":
        return {"status": "pending", "message": "Waiting for user to sign in..."}

    return {
        "status": "linked",
        "token": data.get("token"),
        "email": data.get("email", ""),
    }


def _success_page(email: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Linked</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #faf8f5;
            color: #1a1714;
        }}
        .card {{
            text-align: center;
            padding: 48px;
            background: white;
            border-radius: 24px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.06);
            max-width: 420px;
        }}
        .icon {{
            width: 64px;
            height: 64px;
            background: #e8f5e9;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            font-size: 28px;
        }}
        h1 {{ font-size: 22px; font-weight: 600; margin-bottom: 8px; }}
        p {{ color: #8a8279; font-size: 14px; line-height: 1.5; }}
        .email {{ color: #1a1714; font-weight: 500; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">✓</div>
        <h1>Account Linked!</h1>
        <p>Signed in as <span class="email">{email}</span></p>
        <p style="margin-top: 16px;">You can close this tab and return to the agent.</p>
    </div>
</body>
</html>"""


def _error_page(message: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Error</title>
    <style>
        body {{
            font-family: -apple-system, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #faf8f5;
        }}
        .card {{
            text-align: center;
            padding: 48px;
            background: white;
            border-radius: 24px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.06);
            max-width: 420px;
        }}
        .icon {{ font-size: 28px; margin-bottom: 16px; }}
        h1 {{ font-size: 20px; margin-bottom: 8px; }}
        p {{ color: #8a8279; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="icon">✗</div>
        <h1>Something went wrong</h1>
        <p>{message}</p>
    </div>
</body>
</html>"""
