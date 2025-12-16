"""
Product Service - Business Logic
"""
from typing import Optional, List, Dict, Any
from decimal import Decimal
from ..core.database import db
from ..models.product import (
    ProductBase, ProductDetail, ProductListResponse,
    Brand, Category, ProductImage, StatsResponse
)


class ProductService:
    """Service for product-related operations"""

    # Brand ID mapping for convenience
    BRAND_IDS = {
        "oneal": 7,
        "o'neal": 7,
        "oakley": 19,
        "lezyne": 13,
        "evs": 14,
        "rekluse": 6,
        "azonic": 18,
        "kini": 25,
        "kini red bull": 25,
    }

    def get_products(
        self,
        brand: Optional[str] = None,
        brand_id: Optional[int] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        active_only: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> ProductListResponse:
        """Get products with filters"""

        # Build WHERE clause
        conditions = []
        params = []

        if active_only:
            conditions.append("a.boolA_NichtMehrLieferbar = 0")

        # Brand filter (by name or ID)
        if brand:
            brand_lower = brand.lower()
            if brand_lower in self.BRAND_IDS:
                brand_id = self.BRAND_IDS[brand_lower]

        if brand_id:
            conditions.append("a.lngA_Marke_FKey = ?")
            params.append(brand_id)

        if category_id:
            conditions.append("a.lngA_AGruppe_FKey = ?")
            params.append(category_id)

        if search:
            conditions.append(
                "(a.strA_Nummer LIKE ? OR a.strA_Bezeichnung LIKE ? OR a.strA_EAN LIKE ?)"
            )
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Count total
        count_query = f"""
            SELECT COUNT(*) FROM dbo.tblArtikel a WHERE {where_clause}
        """
        total = db.execute_scalar(count_query, tuple(params) if params else None)

        # Get products (OFFSET/FETCH for SQL Server pagination)
        query = f"""
            SELECT
                a.lngA_Key AS id,
                a.strA_Nummer AS nummer,
                a.strA_Bezeichnung AS bezeichnung,
                a.lngA_Marke_FKey AS brand_id,
                m.strMk_Marke AS brand_name,
                a.lngA_AGruppe_FKey AS category_id,
                g.strAGruppe_Name AS category_name,
                a.decA_Netto AS netto_eur,
                a.strA_EAN AS ean,
                CASE WHEN a.boolA_NichtMehrLieferbar = 0 THEN 1 ELSE 0 END AS active
            FROM dbo.tblArtikel a
            LEFT JOIN dbo.listMarken m ON a.lngA_Marke_FKey = m.lngMk_Key
            LEFT JOIN dbo.listArtikelgruppen g ON a.lngA_AGruppe_FKey = g.lngAGruppe_Key
            WHERE {where_clause}
            ORDER BY a.strA_Nummer
            OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY
        """

        rows = db.execute_query(query, tuple(params) if params else None)

        items = [
            ProductBase(
                id=row["id"],
                nummer=row["nummer"],
                bezeichnung=row["bezeichnung"],
                brand_id=row["brand_id"],
                brand_name=row["brand_name"],
                category_id=row["category_id"],
                category_name=row["category_name"],
                netto_eur=Decimal(str(row["netto_eur"] or 0)),
                ean=row["ean"],
                active=bool(row["active"]),
            )
            for row in rows
        ]

        return ProductListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + len(items)) < total,
        )

    def get_product_by_nummer(self, nummer: str) -> Optional[ProductDetail]:
        """Get single product by article number"""

        query = """
            SELECT
                a.lngA_Key AS id,
                a.strA_Nummer AS nummer,
                a.strA_Bezeichnung AS bezeichnung,
                a.lngA_Marke_FKey AS brand_id,
                m.strMk_Marke AS brand_name,
                a.lngA_AGruppe_FKey AS category_id,
                g.strAGruppe_Name AS category_name,
                a.decA_Netto AS netto_eur,
                a.decA_Brutto AS brutto_eur,
                a.decA_HEK AS hek_eur,
                p.decA_Netto_SFR AS netto_chf,
                p.decA_Netto_USD AS netto_usd,
                a.strA_EAN AS ean,
                a.decA_GewichtInGramm AS gewicht_gramm,
                a.strA_Zolltarifnummer AS zolltarifnummer,
                l.strLand_Name AS herkunftsland,
                a.strA_Bildpfad AS hauptbild,
                a.strA_Artikeltext_kurz AS artikeltext_kurz,
                a.strA_Artikeltext_lang AS artikeltext_lang,
                z.lngAZI_Modelljahr AS modelljahr,
                z.strAZI_ASIN AS asin,
                a.datA_Anlagedatum AS created_at,
                CASE WHEN a.boolA_NichtMehrLieferbar = 0 THEN 1 ELSE 0 END AS active
            FROM dbo.tblArtikel a
            LEFT JOIN dbo.listMarken m ON a.lngA_Marke_FKey = m.lngMk_Key
            LEFT JOIN dbo.listArtikelgruppen g ON a.lngA_AGruppe_FKey = g.lngAGruppe_Key
            LEFT JOIN dbo.tblArtikelPreise p ON a.lngA_Key = p.lngAPR_A_FKey
            LEFT JOIN dbo.tblArtikelZusatzInfo z ON a.lngA_Key = z.lngAZI_A_FKey
            LEFT JOIN dbo.listLaender l ON a.lngA_Herkunftsland_FKey = l.lngLand_Key
            WHERE a.strA_Nummer = ?
        """

        rows = db.execute_query(query, (nummer,))
        if not rows:
            return None

        row = rows[0]

        # Get images
        img_query = """
            SELECT strAB_Bildpfad AS path, lngAB_Sortierung AS sort
            FROM dbo.tblArtikelBildpfade
            WHERE lngAB_A_FKey = ?
            ORDER BY lngAB_Sortierung
        """
        img_rows = db.execute_query(img_query, (row["id"],))
        images = [ProductImage(path=r["path"], sort=r["sort"] or 1) for r in img_rows]

        return ProductDetail(
            id=row["id"],
            nummer=row["nummer"],
            bezeichnung=row["bezeichnung"],
            brand_id=row["brand_id"],
            brand_name=row["brand_name"],
            category_id=row["category_id"],
            category_name=row["category_name"],
            netto_eur=Decimal(str(row["netto_eur"] or 0)),
            brutto_eur=Decimal(str(row["brutto_eur"])) if row["brutto_eur"] else None,
            hek_eur=Decimal(str(row["hek_eur"])) if row["hek_eur"] else None,
            netto_chf=Decimal(str(row["netto_chf"])) if row["netto_chf"] else None,
            netto_usd=Decimal(str(row["netto_usd"])) if row["netto_usd"] else None,
            ean=row["ean"],
            gewicht_gramm=Decimal(str(row["gewicht_gramm"])) if row["gewicht_gramm"] else None,
            zolltarifnummer=row["zolltarifnummer"],
            herkunftsland=row["herkunftsland"],
            hauptbild=row["hauptbild"],
            images=images,
            artikeltext_kurz=row["artikeltext_kurz"],
            artikeltext_lang=row["artikeltext_lang"],
            modelljahr=row["modelljahr"],
            asin=row["asin"],
            created_at=str(row["created_at"]) if row["created_at"] else None,
            active=bool(row["active"]),
        )

    def get_brands(self) -> List[Brand]:
        """Get all brands with article counts"""
        query = """
            SELECT
                m.lngMk_Key,
                m.strMk_Marke,
                COUNT(a.lngA_Key) AS article_count
            FROM dbo.listMarken m
            LEFT JOIN dbo.tblArtikel a ON m.lngMk_Key = a.lngA_Marke_FKey
                AND a.boolA_NichtMehrLieferbar = 0
            GROUP BY m.lngMk_Key, m.strMk_Marke
            HAVING COUNT(a.lngA_Key) > 0
            ORDER BY COUNT(a.lngA_Key) DESC
        """
        rows = db.execute_query(query)
        return [
            Brand(
                lngMk_Key=row["lngMk_Key"],
                strMk_Marke=row["strMk_Marke"],
                article_count=row["article_count"],
            )
            for row in rows
        ]

    def get_categories(self) -> List[Category]:
        """Get all article groups"""
        query = """
            SELECT lngAGruppe_Key, strAGruppe_Name, strAGruppe_Name_GB
            FROM dbo.listArtikelgruppen
            ORDER BY strAGruppe_Name
        """
        rows = db.execute_query(query)
        return [
            Category(
                lngAGruppe_Key=row["lngAGruppe_Key"],
                strAGruppe_Name=row["strAGruppe_Name"],
                strAGruppe_Name_GB=row["strAGruppe_Name_GB"],
            )
            for row in rows
        ]

    def get_stats(self) -> StatsResponse:
        """Get database statistics"""
        total = db.execute_scalar("SELECT COUNT(*) FROM dbo.tblArtikel")
        active = db.execute_scalar(
            "SELECT COUNT(*) FROM dbo.tblArtikel WHERE boolA_NichtMehrLieferbar = 0"
        )
        brands_count = db.execute_scalar("SELECT COUNT(*) FROM dbo.listMarken")
        customers = db.execute_scalar("SELECT COUNT(*) FROM tbl.Trans_tblKunden")

        brands = self.get_brands()

        return StatsResponse(
            total_articles=total,
            active_articles=active,
            total_brands=brands_count,
            total_customers=customers,
            brands=[{"name": b.name, "count": b.article_count} for b in brands[:10]],
        )


# Global instance
product_service = ProductService()
