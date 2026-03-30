from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

# In production, use environment variables!
SECRET_KEY = "ucp_real_secret_key_889"
ALGORITHM = "HS256"

bearer_scheme = HTTPBearer()


def _auth_error(message: str, expired: bool = False):
    """Actionable auth error — tells the agent exactly what to do next."""
    detail = {
        "error": "not_authenticated" if not expired else "token_expired",
        "message": message,
        "action": "Initiate identity linking via the OAuth flow",
        "steps": [
            "Generate a session_id (UUID)",
            "Redirect user to: GET /oauth/authorize?client_id={agent_id}&redirect_uri=/agent/callback?session_id={session_id}&state={session_id}",
            "Poll GET /agent/session/{session_id} every 2 seconds until status='linked'",
            "Use the returned token as: Authorization: Bearer {token}"
        ],
        "discovery_url": "/.well-known/ucp"
    }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
    )


def get_current_user(token: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    """Standard UCP Bearer token verification using JWT."""
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            _auth_error("Token payload missing subject (sub)")
        return user_id
    except jwt.ExpiredSignatureError:
        _auth_error("Token has expired. Re-initiate identity linking.", expired=True)
    except jwt.PyJWTError:
        _auth_error("Invalid Bearer Token. Initiate identity linking to get a valid token.")


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Helper to generate a real JWT for Identity Linking."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
