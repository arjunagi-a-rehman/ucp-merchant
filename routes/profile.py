from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

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
        "name": "Sample UCP Merchant",
        "capabilities": [
            "checkout", 
            "order",
            "dev.ucp.common.identity_linking"
        ]
    }

@router.get("/.well-known/oauth-authorization-server")
def get_oauth_config():
    from .oauth_config import config
    return {
        "issuer": "http://127.0.0.1:8000",
        "authorization_endpoint": "http://127.0.0.1:8000/oauth/authorize",
        "token_endpoint": "http://127.0.0.1:8000/oauth/token"
    }
