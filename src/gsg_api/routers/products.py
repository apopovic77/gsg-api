"""
Product Router - API Endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse

from ..core.auth import verify_api_key
from ..models.product import (
    ProductBase, ProductDetail, ProductListResponse, ProductPretty
)
from ..services.product_service import product_service

router = APIRouter(prefix="/products", tags=["Products"])


def format_product_pretty(p: ProductDetail) -> str:
    """Format product as compact text for AI/MCP"""
    lines = [
        f"{p.nummer} | {p.bezeichnung}",
        f"Marke: {p.brand_name or 'N/A'} | Kat: {p.category_name or 'N/A'}",
        f"Preis: €{p.netto_eur:.2f} netto",
    ]

    if p.brutto_eur:
        lines[-1] += f" / €{p.brutto_eur:.2f} brutto"

    if p.ean:
        lines.append(f"EAN: {p.ean}")

    if p.images:
        img_list = ", ".join([i.path for i in p.images[:3]])
        lines.append(f"Bilder: {img_list}")

    if p.artikeltext_kurz:
        lines.append(f"Info: {p.artikeltext_kurz[:100]}")

    lines.append(f"Status: {'lieferbar' if p.active else 'nicht lieferbar'}")

    return "\n".join(lines)


def format_list_pretty(products: ProductListResponse) -> str:
    """Format product list as compact text"""
    lines = [
        f"Produkte: {products.total} gefunden (zeige {len(products.items)})",
        "-" * 50,
    ]

    for p in products.items:
        status = "✓" if p.active else "✗"
        lines.append(
            f"{status} {p.nummer} | {p.bezeichnung[:40]} | {p.brand_name} | €{p.netto_eur:.2f}"
        )

    if products.has_more:
        lines.append(f"... und {products.total - products.offset - len(products.items)} weitere")

    return "\n".join(lines)


@router.get("", response_model=ProductListResponse)
async def list_products(
    brand: Optional[str] = Query(None, description="Filter by brand name (e.g., 'oneal')"),
    brand_id: Optional[int] = Query(None, description="Filter by brand ID"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search in number, name, EAN"),
    active: bool = Query(True, description="Only active/available products"),
    limit: int = Query(50, ge=1, le=500, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    format: str = Query("json", description="Response format: json or pretty"),
    _api_key: str = Depends(verify_api_key),
):
    """
    List products with optional filters.

    **Brands:** oneal, oakley, lezyne, evs, rekluse, azonic, kini

    **Format:**
    - `json`: Full JSON response (default)
    - `pretty`: Compact text format for AI/MCP
    """
    result = product_service.get_products(
        brand=brand,
        brand_id=brand_id,
        category_id=category_id,
        search=search,
        active_only=active,
        limit=limit,
        offset=offset,
    )

    if format == "pretty":
        return PlainTextResponse(format_list_pretty(result))

    return result


@router.get("/{nummer}", response_model=ProductDetail)
async def get_product(
    nummer: str,
    format: str = Query("json", description="Response format: json or pretty"),
    _api_key: str = Depends(verify_api_key),
):
    """
    Get single product by article number.

    **Example:** GET /products/0781-012
    """
    product = product_service.get_product_by_nummer(nummer)

    if not product:
        raise HTTPException(status_code=404, detail=f"Product {nummer} not found")

    if format == "pretty":
        return PlainTextResponse(format_product_pretty(product))

    return product
