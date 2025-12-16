# GSG API - Claude Context

## Projektübersicht

**GSG API** ist eine FastAPI-basierte REST API für die Gravity Sports Group (O'Neal Europe).
Sie bietet Zugriff auf die LIUS ERP-Datenbank mit Produkten, Marken und Kategorien.

## Architektur

```
src/gsg_api/
├── main.py              # FastAPI App Entry
├── core/
│   ├── config.py        # Settings (pydantic-settings)
│   ├── auth.py          # API Key Authentication
│   └── database.py      # MSSQL Connection Manager
├── routers/
│   ├── products.py      # Product endpoints
│   └── brands.py        # Brands & categories
├── models/
│   └── product.py       # Pydantic models
└── services/
    └── product_service.py  # Business logic
```

## Datenbank

- **Server:** Microsoft SQL Server 2016 SP2
- **Host:** 192.168.2.63
- **Database:** lius
- **Driver:** ODBC Driver 18 for SQL Server

### Wichtige Tabellen

| Tabelle | Beschreibung |
|---------|--------------|
| `dbo.tblArtikel` | Artikel-Stammdaten (47.809) |
| `dbo.listMarken` | Marken (23) |
| `dbo.listArtikelgruppen` | Kategorien |
| `dbo.tblArtikelBildpfade` | Produktbilder |
| `dbo.tblArtikelPreise` | Preise in EUR/CHF/USD |

### Haupt-Marke

**O'Neal (ID: 7)** = 33.493 Artikel (70% des Sortiments)

## API Design

### Authentication

- Header: `x-api-key`
- Keys in `.env` als komma-separierte Liste

### Response Formate

1. **JSON** (default): Vollständiges JSON
2. **Pretty** (`?format=pretty`): Kompakter Text für AI/MCP

### Endpoints

```
GET /products            - Liste mit Filtern
GET /products/{nummer}   - Einzelprodukt
GET /brands              - Alle Marken
GET /categories          - Alle Kategorien
GET /stats               - Statistiken
GET /health              - Health Check
```

## Entwicklung

```bash
# Virtuelle Umgebung
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Server starten
python -m uvicorn src.gsg_api.main:app --reload

# Docs öffnen
http://localhost:8000/docs
```

## Deployment

Server: aiserver.oneal.eu (172.16.255.20)
Service: gsg-api.service (systemd)
Port: 8000

```bash
.devops/scripts/deploy-to-server.sh --server aiserver
```
