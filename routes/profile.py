from fastapi import APIRouter, Request
from config import STOREFRONT_URL

router = APIRouter(tags=["profile"])


@router.get("/.well-known/ucp", summary="UCP Discovery Profile")
def get_ucp_profile(request: Request):
    """
    Entry point for the Universal Commerce Protocol.
    AI agents query this URL to discover capabilities, flows, endpoints, and schemas.
    This is the ONLY URL an agent needs — everything else is discovered from here.
    """
    base = str(request.base_url).rstrip("/")

    return {
        "version": "1.0",
        "name": "UCP Demo Store",
        "description": "An online store selling electronics, fashion, and home products. Prices in INR.",
        "currency": "INR",
        "capabilities": ["products", "checkout", "orders", "identity_linking"],

        # Machine-readable flow definitions
        "flows": {
            "browse": {
                "description": "Browse and search the product catalog",
                "steps": ["list_products"],
                "endpoints": {
                    "list_products": {
                        "method": "GET",
                        "path": "/products",
                        "auth_required": False,
                        "params": {
                            "category": {"type": "string", "required": False, "description": "Filter by category (electronics, fashion, home)"}
                        },
                        "response": {
                            "type": "array",
                            "item_fields": ["id", "name", "price", "category", "description", "inventory", "imageUrl"]
                        }
                    },
                    "get_product": {
                        "method": "GET",
                        "path": "/products/{product_id}",
                        "auth_required": False
                    }
                }
            },

            "identity_linking": {
                "description": "Link user's identity via OAuth 2.0 with agent polling pattern",
                "method": "oauth2_agent_polling",
                "steps": ["generate_session_id", "redirect_user_to_login", "poll_for_token"],
                "login_url_template": f"{base}/oauth/authorize?client_id={{agent_id}}&redirect_uri={base}/agent/callback?session_id={{session_id}}&state={{session_id}}",
                "poll_endpoint": f"{base}/agent/session/{{session_id}}",
                "poll_interval_ms": 2000,
                "poll_max_attempts": 30,
                "token_type": "Bearer",
                "token_lifetime_seconds": 3600,
                "poll_response": {
                    "pending": {"status": "pending"},
                    "success": {"status": "linked", "token": "<jwt>", "email": "<user_email>"}
                }
            },

            "purchase": {
                "description": "Complete purchase flow: create session → add buyer info → complete",
                "auth_required": True,
                "steps": [
                    {
                        "name": "create_session",
                        "method": "POST",
                        "path": "/checkout/sessions",
                        "description": "Create a checkout session with items from the catalog",
                        "request_body": {
                            "line_items": {
                                "type": "array",
                                "items": {
                                    "id": {"type": "string", "description": "Product ID from /products", "maps_to": "product.id"},
                                    "name": {"type": "string", "description": "Product name", "maps_to": "product.name"},
                                    "quantity": {"type": "integer", "description": "Number to purchase"},
                                    "price": {"type": "number", "description": "Unit price in INR", "maps_to": "product.price"}
                                }
                            }
                        },
                        "response_status": "incomplete",
                        "next_step": "update_buyer"
                    },
                    {
                        "name": "update_buyer",
                        "method": "POST",
                        "path": "/checkout/sessions/{session_id}/update",
                        "description": "Add buyer shipping and payment info",
                        "request_body": {
                            "buyer": {
                                "email": {"type": "string", "required": True},
                                "shipping_address": {
                                    "street": {"type": "string", "required": False},
                                    "city": {"type": "string", "required": True},
                                    "state": {"type": "string", "required": True},
                                    "zip": {"type": "string", "required": False}
                                },
                                "payment_method": {"type": "string", "default": "razorpay", "description": "Use 'razorpay' for this merchant"}
                            }
                        },
                        "response_status": "ready_for_complete",
                        "next_step": "complete"
                    },
                    {
                        "name": "complete",
                        "method": "POST",
                        "path": "/checkout/sessions/{session_id}/complete",
                        "description": "Finalize the purchase and create the order",
                        "response_status": "complete",
                        "response_includes": ["order_id"]
                    }
                ]
            },

            "order_tracking": {
                "description": "Check order status after purchase",
                "auth_required": True,
                "endpoints": {
                    "get_order": {
                        "method": "GET",
                        "path": "/orders/{order_id}",
                        "response_fields": ["id", "status", "line_items", "buyer", "total", "tracking_url"]
                    },
                    "list_orders": {
                        "method": "GET",
                        "path": "/orders",
                        "description": "List all orders for the authenticated user"
                    }
                }
            }
        },

        # OpenAPI spec location
        "openapi_url": f"{base}/openapi.json",

        # OAuth config
        "oauth": {
            "authorization_endpoint": f"{base}/oauth/authorize",
            "token_endpoint": f"{base}/oauth/token",
            "agent_callback_endpoint": f"{base}/agent/callback",
            "agent_session_endpoint": f"{base}/agent/session/{{session_id}}"
        }
    }


@router.get("/.well-known/oauth-authorization-server")
def get_oauth_config(request: Request):
    base = str(request.base_url).rstrip("/")
    return {
        "issuer": base,
        "authorization_endpoint": f"{base}/oauth/authorize",
        "token_endpoint": f"{base}/oauth/token"
    }
