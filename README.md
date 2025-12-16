# GSG API

**Gravity Sports Group Product API** - FastAPI-based REST API for O'Neal, Lezyne, EVS and other GSG brands.

## Features

- **Product Catalog**: Full product database with 47k+ articles
- **Multi-Brand**: O'Neal (33k), Oakley, Lezyne, EVS, Rekluse, Azonic, Kini Red Bull
- **API Key Auth**: Secure access via `x-api-key` header
- **Pretty Mode**: AI/MCP-optimized compact text responses
- **SQL Server**: Direct connection to LIUS ERP system

## Quick Start

```bash
# Clone
git clone https://github.com/apopovic77/gsg-api.git
cd gsg-api

# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run
python -m uvicorn src.gsg_api.main:app --reload
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /products` | List products with filters |
| `GET /products/{nummer}` | Get product by article number |
| `GET /brands` | List all brands |
| `GET /categories` | List all categories |
| `GET /stats` | Database statistics |
| `GET /health` | Health check |

## Authentication

All endpoints require `x-api-key` header:

```bash
curl -H "x-api-key: your-key" https://api.example.com/products
```

## Query Parameters

### Products List

| Param | Type | Description |
|-------|------|-------------|
| `brand` | string | Filter by brand name (e.g., "oneal") |
| `brand_id` | int | Filter by brand ID |
| `category_id` | int | Filter by category ID |
| `search` | string | Search in number, name, EAN |
| `active` | bool | Only active products (default: true) |
| `limit` | int | Max results (default: 50, max: 500) |
| `offset` | int | Pagination offset |
| `format` | string | "json" or "pretty" |

## Pretty Format

For AI/MCP consumers, use `?format=pretty` for compact text responses:

```
GET /products/0781-012?format=pretty

0781-012 | Nemora Vest V.27 orange S
Marke: O'Neal | Kat: Protektoren
Preis: €45.00 netto / €53.55 brutto
EAN: 4046068706924
Bilder: 0781-01_front.png, 0781-01_back.png
Status: lieferbar
```

## Brands

| ID | Brand | Articles |
|----|-------|----------|
| 7 | O'Neal | 33,493 |
| 19 | Oakley | 3,946 |
| 13 | Lezyne | 705 |
| 14 | EVS | 549 |
| 6 | Rekluse | 639 |
| 18 | Azonic | 752 |
| 25 | Kini Red Bull | 354 |

## Development

```bash
# Run with auto-reload
uvicorn src.gsg_api.main:app --reload --host 0.0.0.0 --port 8000

# Access docs
open http://localhost:8000/docs
```

## Deployment

Uses DevOps scripts from github-starterpack:

```bash
.devops/scripts/deploy-to-server.sh --server aiserver
```

## License

Proprietary - Gravity Sports Group

---

Built with FastAPI | Powered by LIUS ERP
