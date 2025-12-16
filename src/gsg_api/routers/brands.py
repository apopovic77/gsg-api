"""
Brands & Categories Router
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse

from ..core.auth import verify_api_key
from ..models.product import Brand, Category, StatsResponse
from ..services.product_service import product_service

router = APIRouter(tags=["Brands & Categories"])


@router.get("/brands", response_model=List[Brand])
async def list_brands(
    format: str = Query("json", description="Response format: json or pretty"),
    _api_key: str = Depends(verify_api_key),
):
    """
    List all brands with article counts.

    Returns brands sorted by article count (descending).
    """
    brands = product_service.get_brands()

    if format == "pretty":
        lines = ["Marken:", "-" * 30]
        for b in brands:
            lines.append(f"  [{b.id:2}] {b.name}: {b.article_count} Artikel")
        return PlainTextResponse("\n".join(lines))

    return brands


@router.get("/categories", response_model=List[Category])
async def list_categories(
    format: str = Query("json", description="Response format: json or pretty"),
    _api_key: str = Depends(verify_api_key),
):
    """
    List all article categories.
    """
    categories = product_service.get_categories()

    if format == "pretty":
        lines = ["Kategorien:", "-" * 30]
        for c in categories:
            name_en = f" ({c.name_en})" if c.name_en else ""
            lines.append(f"  [{c.id:3}] {c.name}{name_en}")
        return PlainTextResponse("\n".join(lines))

    return categories


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    format: str = Query("json", description="Response format: json or pretty"),
    _api_key: str = Depends(verify_api_key),
):
    """
    Get database statistics and overview.

    Perfect for AI to understand the data scope.
    """
    stats = product_service.get_stats()

    if format == "pretty":
        lines = [
            "GSG Datenbank Statistiken",
            "=" * 40,
            f"Artikel gesamt:  {stats.total_articles:,}",
            f"Artikel aktiv:   {stats.active_articles:,}",
            f"Marken:          {stats.total_brands}",
            f"Kunden:          {stats.total_customers:,}",
            "",
            "Top Marken:",
        ]
        for b in stats.brands:
            pct = (b["count"] / stats.active_articles * 100) if stats.active_articles else 0
            lines.append(f"  {b['name']}: {b['count']:,} ({pct:.1f}%)")
        return PlainTextResponse("\n".join(lines))

    return stats
