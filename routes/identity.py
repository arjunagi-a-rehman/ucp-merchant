from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
from datetime import timedelta
from security import create_access_token

router = APIRouter(tags=["identity"])

@router.get("/oauth/authorize")
def authorize(
    client_id: str, 
    redirect_uri: str, 
    response_type: str = "code", 
    state: str = None
):
    # In a real app, this would show a LOGIN PAGE.
    # Here, we instantly redirect back with a mock 'auth_code'
    auth_code = "mock_auth_code_987"
    sep = "&" if "?" in redirect_uri else "?"
    url = f"{redirect_uri}{sep}code={auth_code}"
    if state:
        url += f"&state={state}"
    return RedirectResponse(url)

@router.post("/oauth/token")
def token(
    grant_type: str = Form(...),
    code: str = Form(None),
    client_id: str = Form(None),
    client_secret: str = Form(None)
):
    # Standard UCP OAuth Token Exchange
    if code == "mock_auth_code_987":
        # Create a real, signed JWT
        access_token = create_access_token(
            data={"sub": "user_12345", "client_id": client_id},
            expires_delta=timedelta(hours=1)
        )
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600
        }
    return {"error": "invalid_grant"}

@router.get("/callback")
def callback(code: str):
    return {
        "status": "success",
        "message": "Identity linking successful!",
        "auth_code": code,
        "next_step": "Poster this code to /oauth/token to get your access token"
    }
