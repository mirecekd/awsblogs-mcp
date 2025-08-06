# AWS Blogs MCP Server

MCP server pro práci s AWS Blog a News články z [api.aws-news.com](https://api.aws-news.com/articles).

<div align="center">
  
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/mirecekdg)

</div>

## Popis

Tento MCP server poskytuje nástroje pro získávání a filtrování AWS blogových článků a news ze všech AWS kategorií. Server je vytvořen pomocí FastMCP frameworku a podporuje HTTP transport na portu 8807.

## Dostupné MCP nástroje

### 1. `get_todays_posts`
Získá články publikované dnes.

**Parametry:**
- `post_type`: "News", "Blog", nebo "Both" (výchozí)
- `limit`: Maximální počet článků (výchozí 20)

### 2. `get_posts_by_date`
Získá články z konkrétního datového rozsahu.

**Parametry:**
- `from_date`: Datum od ve formátu YYYY-MM-DD (volitelné)
- `to_date`: Datum do ve formátu YYYY-MM-DD (volitelné)
- `days_back`: Počet dní zpět od dneška (alternativa k from_date)
- `post_type`: "News", "Blog", nebo "Both" (výchozí)
- `limit`: Maximální počet článků (výchozí 50)

### 3. `get_posts_by_category`
Získá články z konkrétní kategorie.

**Parametry:**
- `category`: Název kategorie (např. "Big Data", "Machine Learning", "Industries")
- `post_type`: "News", "Blog", nebo "Both" (výchozí)
- `days_back`: Počet dní zpět od dneška (výchozí 30)
- `limit`: Maximální počet článků (výchozí 30)

### 4. `search_posts`
Vyhledá články podle textového dotazu.

**Parametry:**
- `query`: Vyhledávací dotaz (hledá se v názvu, URL a slug)
- `post_type`: "News", "Blog", nebo "Both" (výchozí)
- `days_back`: Počet dní zpět od dneška (výchozí 90)
- `limit`: Maximální počet článků (výchozí 25)

### 5. `get_categories`
Získá seznam všech dostupných kategorií článků.

### 6. `get_latest_posts`
Získá nejnovější články.

**Parametry:**
- `post_type`: "News", "Blog", nebo "Both" (výchozí)
- `limit`: Maximální počet článků (výchozí 20)
- `days_back`: Počet dní zpět od dneška (výchozí 7)

### 7. `get_popular_posts`
Získá populární články (označené jako popular=true).

**Parametry:**
- `post_type`: "News", "Blog", nebo "Both" (výchozí)
- `days_back`: Počet dní zpět od dneška (výchozí 30)
- `limit`: Maximální počet článků (výchozí 15)

### 8. `get_article_content`
Stáhne plný obsah článku z daného URL.

**Parametry:**
- `url`: URL článku (lze získat z ostatních nástrojů)

**Návratové hodnoty:**
- `title`: Titulek článku
- `content`: Plný text článku
- `description`: Meta popis
- `author`: Autor (pokud je dostupný)
- `published_date`: Datum publikace
- `content_length`: Délka obsahu v znacích
- `word_count`: Počet slov

## Dostupné kategorie

Server podporuje filtrování podle těchto kategorií (a dalších):
- Big Data
- Machine Learning
- Business Intelligence
- Industries
- Public Sector
- Media
- AWS News
- Database
- Migration and Modernization
- Training & Certification
- Open Source
- AWS Partner Network
- Integration & Automation
- Messaging & Targeting
- AWS Cloud Operations

## Instalace a spuštění

### Docker (doporučeno)

1. **Spuštění z GitHub Container Registry:**
   ```bash
   docker run -p 8807:8807 ghcr.io/mirecekd/awsblogs-mcp
   ```

2. **Build Docker image lokálně:**
   ```bash
   chmod +x build.sh
   ./build.sh
   ```

3. **Spuštění pomocí docker-compose:**
   ```bash
   docker-compose up awsblogs-mcp-http
   ```

4. **Nebo lokální Docker build:**
   ```bash
   docker run -p 8807:8807 awsblogs-mcp-server:http
   ```

### Lokální vývoj

1. **Instalace závislostí:**
   ```bash
   pip install -e .
   ```

2. **Spuštění serveru:**
   ```bash
   python main_http.py --host 0.0.0.0 --port 8807
   ```

## Konfigurace MCP klienta

Pro použití v MCP klientu (např. Cline) přidejte do konfigurace:

```json
{
  "mcpServers": {
    "awsblogs": {
      "command": "docker",
      "args": ["run", "-p", "8807:8807", "ghcr.io/mirecekd/awsblogs-mcp"],
      "transport": "http",
      "baseUrl": "http://localhost:8807"
    }
  }
}
```

## API Endpoint

Server využívá veřejné API: `https://api.aws-news.com/articles`

## Funkce

- ✅ HTTP transport na portu 8807
- ✅ Filtrování podle typu článku (News/Blog)
- ✅ Filtrování podle kategorie
- ✅ Datové filtrování (rozsah datumů, dny zpět)
- ✅ Textové vyhledávání
- ✅ Cache mechanismus (5 minut)
- ✅ Strukturované odpovědi
- ✅ Docker podpora

## Struktura projektu

```
awsblogs-mcp/
├── src/awsblogs_mcp_server/
│   ├── __init__.py
│   ├── server_http.py          # HTTP MCP server
│   └── data_processor.py       # API client a data processing
├── main_http.py               # HTTP entry point
├── Dockerfile.http            # Docker image pro HTTP
├── docker-compose.yml         # Docker Compose konfigurace
├── build.sh                   # Build script
├── pyproject.toml             # Python projekt konfigurace
└── README.md                  # Tento soubor
```

## Vývoj

Pro vývoj doporučujeme:

1. Fork repository
2. Vytvoření nové větve pro funkci
3. Testování lokálně pomocí `python main_http.py`
4. Testování Docker buildu pomocí `./build.sh`
5. Vytvoření pull requestu

## Licence

MIT License - viz LICENSE soubor.

## Autor

Miroslav Dvořák (mirecekd@gmail.com)

## Inspirace

Projekt inspirován [aws-news-mcp-server](https://github.com/jritsema/aws-news-mcp-server) od jritsema.
