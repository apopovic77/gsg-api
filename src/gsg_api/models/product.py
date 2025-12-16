"""
Product Models (Pydantic)
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal


class Brand(BaseModel):
    """Brand/Marke model"""
    id: int = Field(..., alias="lngMk_Key")
    name: str = Field(..., alias="strMk_Marke")
    article_count: Optional[int] = None

    class Config:
        populate_by_name = True


class Category(BaseModel):
    """Article group/Artikelgruppe model"""
    id: int = Field(..., alias="lngAGruppe_Key")
    name: str = Field(..., alias="strAGruppe_Name")
    name_en: Optional[str] = Field(None, alias="strAGruppe_Name_GB")

    class Config:
        populate_by_name = True


class ProductImage(BaseModel):
    """Product image reference"""
    path: str
    sort: int = 1


class ProductPrice(BaseModel):
    """Product pricing"""
    netto_eur: Decimal
    brutto_eur: Optional[Decimal] = None
    hek_eur: Optional[Decimal] = None
    netto_chf: Optional[Decimal] = None
    netto_usd: Optional[Decimal] = None


class ProductBase(BaseModel):
    """Base product model (list view)"""
    id: int
    nummer: str
    bezeichnung: str
    brand_id: int
    brand_name: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    netto_eur: Decimal
    ean: Optional[str] = None
    active: bool = True


class ProductDetail(ProductBase):
    """Full product model (detail view)"""
    brutto_eur: Optional[Decimal] = None
    hek_eur: Optional[Decimal] = None
    netto_chf: Optional[Decimal] = None
    netto_usd: Optional[Decimal] = None
    gewicht_gramm: Optional[Decimal] = None
    zolltarifnummer: Optional[str] = None
    herkunftsland: Optional[str] = None
    hauptbild: Optional[str] = None
    images: List[ProductImage] = []
    artikeltext_kurz: Optional[str] = None
    artikeltext_lang: Optional[str] = None
    modelljahr: Optional[int] = None
    asin: Optional[str] = None
    created_at: Optional[str] = None


class ProductListResponse(BaseModel):
    """Paginated product list response"""
    items: List[ProductBase]
    total: int
    limit: int
    offset: int
    has_more: bool


class ProductPretty(BaseModel):
    """
    KI-optimiertes kompaktes Format.
    Für MCP/AI mit weniger Tokens.
    """
    text: str  # Human-readable formatted text


class StatsResponse(BaseModel):
    """Database statistics"""
    total_articles: int
    active_articles: int
    total_brands: int
    total_customers: int
    brands: List[dict]
