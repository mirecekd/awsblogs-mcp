# AWS Blogs MCP Server

MCP server for working with AWS Blog and News articles from [api.aws-news.com](https://api.aws-news.com/articles).

<div align="center">
  
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/mirecekdg)

</div>

## Description

This MCP server provides tools for retrieving and filtering AWS blog articles and news from all AWS categories. The server is built using the FastMCP framework, is fully asynchronous (async/await), and supports SSE transport on port 8807. Data is fetched from the public API and processed using aiohttp and BeautifulSoup.

## Architecture

- **Entrypoint:** `main_sse.py` – sets up the environment and starts the server.
- **Server:** `src/awsblogs_mcp_server/server_sse.py` – defines all MCP tools, handles argument parsing, and runs the FastMCP server.
- **Data Processor:** `src/awsblogs_mcp_server/data_processor.py` – handles API communication, filtering, caching, and HTML parsing.
- **Caching:** In-memory cache (5 minutes) for article lists (except search queries, which always fetch fresh data).
- **Validation:** Input parameters are validated for type, presence, and (where relevant) format. Only AWS articles (aws.amazon.com) are supported for full content download.

## Available MCP Tools

### 1. `get_todays_posts`
Gets articles published today.

**Parameters:**
- `post_type`: "News", "Blog", or "Both" (default)
- `limit`: Maximum number of articles (default 20)

### 2. `get_posts_by_date`
Gets articles from a specific date range.

**Parameters:**
- `from_date`: From date in YYYY-MM-DD format (optional)
- `to_date`: To date in YYYY-MM-DD format (optional)
- `days_back`: Number of days back from today (alternative to from_date)
- `post_type`: "News", "Blog", or "Both" (default)
- `limit`: Maximum number of articles (default 50)

### 3. `get_posts_by_category`
Gets articles from a specific category.

**Parameters:**
- `category`: Category name (e.g., "Big Data", "Machine Learning", "Industries")
- `post_type`: "News", "Blog", or "Both" (default)
- `days_back`: Number of days back from today (default 30)
- `limit`: Maximum number of articles (default 30)

### 4. `search_posts`
Searches articles by text query using the API's search functionality (searches in title, URL, and slug).

**Parameters:**
- `query`: Search query (searches in title, URL, and slug)
- `post_type`: "News", "Blog", or "Both" (default)
- `days_back`: Number of days back from today (default 90)
- `limit`: Maximum number of articles (default 25)

**Note:** Search queries always fetch fresh data and do not use cache.

### 5. `get_categories`
Gets a list of all available article categories.

### 6. `get_latest_posts`
Gets the latest articles.

**Parameters:**
- `post_type`: "News", "Blog", or "Both" (default)
- `limit`: Maximum number of articles (default 20)
- `days_back`: Number of days back from today (default 7)

### 7. `get_popular_posts`
Gets popular articles (marked as popular=true).

**Parameters:**
- `post_type`: "News", "Blog", or "Both" (default)
- `days_back`: Number of days back from today (default 30)
- `limit`: Maximum number of articles (default 15)

### 8. `get_article_content`
Downloads full article content from a given URL.

**Parameters:**
- `url`: Article URL (must be from aws.amazon.com)

**Return values:**
- `title`: Article title
- `content`: Full article text
- `description`: Meta description
- `author`: Author (if available)
- `published_date`: Publication date
- `content_length`: Content length in characters
- `word_count`: Word count

**Note:** Only AWS articles (aws.amazon.com) are supported for full content download.

## Available Categories

The server supports filtering by these categories:
- Architecture
- AWS Cloud Operations
- AWS for Games
- AWS Insights
- AWS Marketplace
- AWS News
- AWS Partner Network
- AWS Smart Business
- Big Data
- Business Intelligence
- Business Productivity
- Cloud Enterprise Strategy
- Cloud Financial Management
- Compute
- Contact Center
- Containers
- Database
- Desktop & Application Streaming
- Developer Tools
- DevOps & Developer Productivity
- Front-End Web & Mobile
- HPC
- IBM and Red Hat
- Industries
- Integration & Automation
- Internet of Things
- Machine Learning
- Media
- Messaging & Targeting
- Microsoft Workloads on AWS
- Migration and Modernization
- .NET on AWS
- Networking & Content Delivery
- Open Source
- Public Sector
- Quantum Computing
- SAP
- Security
- Spatial Computing
- Startups
- Storage
- Supply Chain & Logistics
- Training & Certification

## Caching

- Article lists are cached in memory for 5 minutes (except for search queries).
- Search queries always fetch fresh data from the API.
- Cache is invalidated automatically after timeout or when parameters change.

## Installation and Running

### Docker (recommended)

1. **Run from GitHub Container Registry:**
   ```bash
   docker run -p 8807:8807 ghcr.io/mirecekd/awsblogs-mcp
   ```

2. **Build Docker image locally:**
   ```bash
   chmod +x build.sh
   ./build.sh
   ```

3. **Run using docker-compose:**
   ```bash
   docker-compose up awsblogs-mcp-sse
   ```

4. **Or local Docker build:**
   ```bash
   docker run -p 8807:8807 awsblogs-mcp-server:sse
   ```

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -e .
   ```

2. **Run server:**
   ```bash
   python main_sse.py --host 0.0.0.0 --port 8807
   ```

## MCP Client Configuration

To use in an MCP client (e.g., Cline), add to configuration:

```json
{
  "mcpServers": {
    "awsblogs": {
      "type": "sse",
      "url": "http://localhost:8807/sse/"
    }
  }
}
```

## API Endpoint

The server uses the public API: `https://api.aws-news.com/articles`

## Features

- ✅ SSE transport on port 8807
- ✅ Filter by article type (News/Blog)
- ✅ Filter by category
- ✅ Date filtering (date range, days back)
- ✅ Text search (API-powered)
- ✅ Cache mechanism (5 minutes, except for search)
- ✅ Structured responses
- ✅ Docker support
- ✅ Asynchronous architecture (aiohttp, FastMCP)
- ✅ HTML parsing with BeautifulSoup

## Project Structure

```
awsblogs-mcp/
├── src/awsblogs_mcp_server/
│   ├── __init__.py
│   ├── server_sse.py          # SSE MCP server (tools, server logic)
│   └── data_processor.py      # API client, filtering, caching, HTML parsing
├── main_sse.py               # SSE entry point
├── Dockerfile.sse            # Docker image for SSE
├── docker-compose.yml        # Docker Compose configuration
├── build.sh                  # Build script
├── pyproject.toml            # Python project configuration
├── README.md                 # This file
└── assets/
    ├── aws_blogs.png
    └── n8n-workflow.json
```

## Development

For development we recommend:

1. Fork the repository
2. Create a new branch for the feature
3. Test locally using `python main_sse.py`
4. Test Docker build using `./build.sh`
5. Create a pull request

## License

MIT License - see LICENSE file.

## Author

Miroslav Dvořák (mirecekd@gmail.com)

## Usage Examples

### N8N Workflow Integration

This MCP server can be easily integrated with N8N workflows for automated AWS news processing and notifications.

![AWS Blogs MCP in N8N](./assets/aws_blogs.png)

The screenshot above shows a real-world N8N workflow where the AWS Blogs MCP server is used as a tool within an AI Agent. The workflow consists of:

1. **Chat Trigger** - Receives user messages
2. **AI Agent** - Processes requests using Azure OpenAI
3. **AWS Blogs MCP Tool** - Fetches AWS articles based on user queries
4. **Memory Buffer** - Maintains conversation context

**Example N8N Workflow:** You can find a complete N8N workflow configuration in [./assets/n8n-workflow.json](./assets/n8n-workflow.json)

**How it works in practice:**
- User asks: "Show me latest AWS articles about Machine Learning"
- AI Agent uses the MCP server to call `search_posts` with query "Machine Learning"
- Server returns relevant AWS ML articles with titles, URLs, and summaries
- AI Agent formats the response for the user with clickable links
- Conversation context is maintained for follow-up questions

This integration allows for natural language interactions with AWS content, making it easy to stay updated with the latest AWS developments through conversational AI.

## Inspiration

Project inspired by [aws-news-mcp-server](https://github.com/jritsema/aws-news-mcp-server) by jritsema.
