import httpx
from fastapi import APIRouter, HTTPException, Request
from config import STOREFRONT_URL

router = APIRouter(prefix="/products", tags=["products"])


def _add_product_actions(product: dict, request: Request) -> dict:
    """Add next_actions to product responses."""
    base = str(request.base_url).rstrip("/")
    product["next_actions"] = [{
        "action": "add_to_checkout",
        "description": "Add this product to a checkout session",
        "method": "POST",
        "endpoint": f"{base}/checkout/sessions",
        "auth_required": True,
        "example_body": {
            "line_items": [{
                "id": product.get("id"),
                "name": product.get("name"),
                "quantity": 1,
                "price": product.get("price")
            }]
        }
    }]
    return product


@router.get("", summary="List Products")
def list_products(request: Request, category: str = None):
    """
    Browse the merchant's product catalog.

    Returns all products with IDs, names, prices (INR), categories, and descriptions.
    Use the product `id` and `price` fields when creating a checkout session.

    **Categories**: electronics, fashion, home
    """
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{STOREFRONT_URL}/api/products")
        resp.raise_for_status()
        products = resp.json()
        if category:
            products = [p for p in products if p.get("category") == category]
        return [_add_product_actions(p, request) for p in products]


@router.get("/{product_id}", summary="Get Product")
def get_product(product_id: str, request: Request):
    """
    Get a single product by ID.

    The response includes `next_actions` showing how to add this product to a checkout.
    """
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{STOREFRONT_URL}/api/products/{product_id}")
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail={
                "error": "Product not found",
                "action": "List all products at GET /products"
            })
        resp.raise_for_status()
        return _add_product_actions(resp.json(), request)
