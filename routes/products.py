import httpx
from fastapi import APIRouter, HTTPException
from config import STOREFRONT_URL

router = APIRouter(prefix="/products", tags=["products"])

@router.get("", summary="List Products")
def list_products(category: str = None):
    """Browse the merchant's product catalog. Optionally filter by category."""
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{STOREFRONT_URL}/api/products")
        resp.raise_for_status()
        products = resp.json()
        if category:
            products = [p for p in products if p.get("category") == category]
        return products

@router.get("/{product_id}", summary="Get Product")
def get_product(product_id: str):
    """Get a single product by ID."""
    with httpx.Client(timeout=30) as client:
        resp = client.get(f"{STOREFRONT_URL}/api/products/{product_id}")
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Product not found")
        resp.raise_for_status()
        return resp.json()
