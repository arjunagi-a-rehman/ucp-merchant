from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List
from config import STOREFRONT_URL, UCP_API_BASE

class UCPProfile(BaseModel):
    version: str
    name: str
    capabilities: List[str]

router = APIRouter(tags=["profile"])

@router.get("/.well-known/ucp", response_model=UCPProfile, summary="Discovery Profile")
def get_ucp_profile():
    """
    Entry point for the Universal Commerce Protocol.
    AI agents query this URL to discover which commerce capabilities (checkout, orders, identity)
    this merchant supports and where their secure configuration is located.
    """
    return {
        "version": "1.0",
        "name": "UCP Demo Store",
        "capabilities": [
            "checkout",
            "order",
            "products",
            "dev.ucp.common.identity_linking"
        ]
    }

@router.get("/.well-known/oauth-authorization-server")
def get_oauth_config(request: Request):
    # Use the request's base URL so it works in any deployment
    base = str(request.base_url).rstrip("/")
    return {
        "issuer": base,
        "authorization_endpoint": f"{base}/oauth/authorize",
        "token_endpoint": f"{base}/oauth/token"
    }
