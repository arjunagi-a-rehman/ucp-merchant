import httpx
from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
from datetime import timedelta
from security import create_access_token
from config import STOREFRONT_URL

FIREBASE_API_KEY = "AIzaSyCCIpMYY-y1weaHjCgmg1ThljFpImjtzrE"

router = APIRouter(tags=["identity"])

@router.get("/oauth/authorize")
def authorize(
    client_id: str,
    redirect_uri: str,
    response_type: str = "code",
    state: str = None
):
    """
    UCP OAuth Authorization endpoint.
    Redirects the user to the merchant's login page (on the storefront)
    where they sign in with Google via Firebase Auth.
    """
    merchant_login_url = (
        f"{STOREFRONT_URL}/login/merchant"
        f"?redirect_uri={redirect_uri}"
        f"&client_id={client_id}"
    )
    if state:
        merchant_login_url += f"&state={state}"

    return RedirectResponse(merchant_login_url)

@router.post("/oauth/token")
def token(
    grant_type: str = Form(...),
    code: str = Form(None),
    client_id: str = Form(None),
    client_secret: str = Form(None)
):
    """
    UCP OAuth Token Exchange.
    The 'code' is a Firebase ID token from the storefront Google sign-in.
    We verify it directly with Firebase and issue a UCP JWT.
    """
    if not code:
        return {"error": "invalid_request", "error_description": "code is required"}

    # Verify the Firebase ID token using Google's tokeninfo endpoint
    with httpx.Client(timeout=10) as client:
        resp = client.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}",
            json={"idToken": code},
        )

    if resp.status_code != 200:
        return {"error": "invalid_grant", "error_description": "Invalid or expired Firebase token"}

    data = resp.json()
    users = data.get("users", [])
    if not users:
        return {"error": "invalid_grant", "error_description": "Could not resolve user"}

    user = users[0]
    uid = user.get("localId")
    email = user.get("email", "")

    if not uid:
        return {"error": "invalid_grant", "error_description": "Could not resolve user ID"}

    # Issue a UCP JWT with the Firebase UID as subject
    access_token = create_access_token(
        data={"sub": uid, "client_id": client_id, "email": email},
        expires_delta=timedelta(hours=1)
    )

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": 3600
    }

@router.get("/callback")
def callback(code: str):
    return {
        "status": "success",
        "message": "Identity linking successful!",
        "auth_code": code,
        "next_step": "POST this code to /oauth/token to get your access token"
    }
