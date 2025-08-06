#!/usr/bin/env python3
"""
AWS Blogs MCP Server - SSE Version
Provides tools for working with AWS Blog and News articles from api.aws-news.com via SSE transport.
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastmcp import FastMCP
from .data_processor import aws_news_api

# Create MCP server with SSE transport
mcp = FastMCP("AWS Blogs and News")

class AWSBlogsError(Exception):
    """Base exception for AWS Blogs operations"""
    pass


class APIError(AWSBlogsError):
    """API communication error"""
    pass


@mcp.tool()
async def get_todays_posts(
    post_type: str = "Both",
    limit: int = 20
) -> Dict[str, Any]:
    """
    Gets articles published today.
    
    Args:
        post_type: Post type - "News", "Blog", or "Both" (default)
        limit: Maximum number of articles (default 20)
    
    Returns:
        Dict containing today's articles
    """
    try:
        # Download all articles
        all_articles = await aws_news_api.fetch_articles()
        
        # Filter today's articles
        todays_articles = aws_news_api.filter_todays_articles(all_articles)
        
        # Filter by type
        filtered_articles = aws_news_api.filter_by_type(todays_articles, post_type)
        
        # Apply limit
        if limit > 0:
            filtered_articles = filtered_articles[:limit]
        
        filters_applied = {
            "date": "today",
            "post_type": post_type,
            "limit": limit
        }
        
        return aws_news_api.format_article_response(filtered_articles, filters_applied)
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting today's posts: {e}",
            "articles": [],
            "total_count": 0
        }


@mcp.tool()
async def get_posts_by_date(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    days_back: Optional[int] = None,
    post_type: str = "Both",
    limit: int = 50
) -> Dict[str, Any]:
    """
    Gets articles from a specific date range.
    
    Args:
        from_date: From date in YYYY-MM-DD format (optional)
        to_date: To date in YYYY-MM-DD format (optional)
        days_back: Number of days back from today (alternative to from_date)
        post_type: Post type - "News", "Blog", or "Both" (default)
        limit: Maximum number of articles (default 50)
    
    Returns:
        Dict containing articles from the given period
    """
    try:
        # Parameter validation
        if days_back and (from_date or to_date):
            return {
                "success": False,
                "error": "Cannot combine days_back with from_date/to_date",
                "articles": [],
                "total_count": 0
            }
        
        if not days_back and not from_date:
            days_back = 7  # Default: week back
        
        # Download all articles
        all_articles = await aws_news_api.fetch_articles()
        
        # Filter by date range
        date_filtered = aws_news_api.filter_by_date_range(
            all_articles, from_date=from_date, to_date=to_date, days_back=days_back
        )
        
        # Filter by type
        type_filtered = aws_news_api.filter_by_type(date_filtered, post_type)
        
        # Apply limit
        if limit > 0:
            type_filtered = type_filtered[:limit]
        
        filters_applied = {
            "from_date": from_date,
            "to_date": to_date,
            "days_back": days_back,
            "post_type": post_type,
            "limit": limit
        }
        
        return aws_news_api.format_article_response(type_filtered, filters_applied)
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting articles by date: {e}",
            "articles": [],
            "total_count": 0
        }


@mcp.tool()
async def get_posts_by_category(
    category: str,
    post_type: str = "Both",
    days_back: int = 30,
    limit: int = 30
) -> Dict[str, Any]:
    """
    Gets articles from a specific category.
    
    Args:
        category: Category name (e.g., "Big Data", "Machine Learning", "Industries")
        post_type: Post type - "News", "Blog", or "Both" (default)
        days_back: Number of days back from today (default 30)
        limit: Maximum number of articles (default 30)
    
    Returns:
        Dict containing articles from the given category
    """
    try:
        # Download all articles
        all_articles = await aws_news_api.fetch_articles()
        
        # Filter by date range
        date_filtered = aws_news_api.filter_by_date_range(all_articles, days_back=days_back)
        
        # Filter by category
        category_filtered = aws_news_api.filter_by_category(date_filtered, category)
        
        # Filter by type
        type_filtered = aws_news_api.filter_by_type(category_filtered, post_type)
        
        # Apply limit
        if limit > 0:
            type_filtered = type_filtered[:limit]
        
        filters_applied = {
            "category": category,
            "post_type": post_type,
            "days_back": days_back,
            "limit": limit
        }
        
        return aws_news_api.format_article_response(type_filtered, filters_applied)
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting articles by category: {e}",
            "articles": [],
            "total_count": 0
        }


@mcp.tool()
async def search_posts(
    query: str,
    post_type: str = "Both",
    days_back: int = 90,
    limit: int = 25
) -> Dict[str, Any]:
    """
    Searches articles by text query.
    
    Args:
        query: Search query (searches in title, URL, and slug)
        post_type: Post type - "News", "Blog", or "Both" (default)
        days_back: Number of days back from today (default 90)
        limit: Maximum number of articles (default 25)
    
    Returns:
        Dict containing found articles
    """
    try:
        if not query.strip():
            return {
                "success": False,
                "error": "Search query cannot be empty",
                "articles": [],
                "total_count": 0
            }
        
        # Download all articles
        all_articles = await aws_news_api.fetch_articles()
        
        # Filter by date range
        date_filtered = aws_news_api.filter_by_date_range(all_articles, days_back=days_back)
        
        # Search by query
        search_filtered = aws_news_api.search_articles(date_filtered, query)
        
        # Filter by type
        type_filtered = aws_news_api.filter_by_type(search_filtered, post_type)
        
        # Apply limit
        if limit > 0:
            type_filtered = type_filtered[:limit]
        
        filters_applied = {
            "query": query,
            "post_type": post_type,
            "days_back": days_back,
            "limit": limit
        }
        
        return aws_news_api.format_article_response(type_filtered, filters_applied)
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error searching articles: {e}",
            "articles": [],
            "total_count": 0
        }


@mcp.tool()
async def get_categories() -> Dict[str, Any]:
    """
    Gets a list of all available article categories.
    
    Returns:
        Dict containing list of categories
    """
    try:
        # Download all articles
        all_articles = await aws_news_api.fetch_articles()
        
        # Get available categories
        categories = aws_news_api.get_available_categories(all_articles)
        
        return {
            "success": True,
            "categories": categories,
            "total_categories": len(categories),
            "message": f"Found {len(categories)} categories"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting categories: {e}",
            "categories": []
        }


@mcp.tool()
async def get_latest_posts(
    post_type: str = "Both",
    limit: int = 20,
    days_back: int = 7
) -> Dict[str, Any]:
    """
    Gets the latest articles.
    
    Args:
        post_type: Post type - "News", "Blog", or "Both" (default)
        limit: Maximum number of articles (default 20)
        days_back: Number of days back from today (default 7)
    
    Returns:
        Dict containing latest articles
    """
    try:
        # Download all articles
        all_articles = await aws_news_api.fetch_articles()
        
        # Filter by date range
        date_filtered = aws_news_api.filter_by_date_range(all_articles, days_back=days_back)
        
        # Filter by type
        type_filtered = aws_news_api.filter_by_type(date_filtered, post_type)
        
        # Sort by publication date (newest first)
        sorted_articles = sorted(
            type_filtered,
            key=lambda x: x.get("published_date", ""),
            reverse=True
        )
        
        # Apply limit
        if limit > 0:
            sorted_articles = sorted_articles[:limit]
        
        filters_applied = {
            "post_type": post_type,
            "days_back": days_back,
            "limit": limit,
            "sort": "newest_first"
        }
        
        return aws_news_api.format_article_response(sorted_articles, filters_applied)
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting latest articles: {e}",
            "articles": [],
            "total_count": 0
        }


@mcp.tool()
async def get_popular_posts(
    post_type: str = "Both",
    days_back: int = 30,
    limit: int = 15
) -> Dict[str, Any]:
    """
    Gets popular articles (marked as popular=true).
    
    Args:
        post_type: Post type - "News", "Blog", or "Both" (default)
        days_back: Number of days back from today (default 30)
        limit: Maximum number of articles (default 15)
    
    Returns:
        Dict containing popular articles
    """
    try:
        # Download all articles
        all_articles = await aws_news_api.fetch_articles()
        
        # Filter by date range
        date_filtered = aws_news_api.filter_by_date_range(all_articles, days_back=days_back)
        
        # Filter by type
        type_filtered = aws_news_api.filter_by_type(date_filtered, post_type)
        
        # Filter only popular articles
        popular_filtered = [
            article for article in type_filtered
            if article.get("popular") == True
        ]
        
        # Sort by publication date (newest first)
        sorted_articles = sorted(
            popular_filtered,
            key=lambda x: x.get("published_date", ""),
            reverse=True
        )
        
        # Apply limit
        if limit > 0:
            sorted_articles = sorted_articles[:limit]
        
        filters_applied = {
            "post_type": post_type,
            "days_back": days_back,
            "limit": limit,
            "popular_only": True
        }
        
        return aws_news_api.format_article_response(sorted_articles, filters_applied)
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting popular articles: {e}",
            "articles": [],
            "total_count": 0
        }


@mcp.tool()
async def get_article_content(url: str) -> Dict[str, Any]:
    """
    Downloads full article content from a given URL.
    
    Args:
        url: Article URL (can be obtained from other tools)
    
    Returns:
        Dict containing full article content including title, author, and meta information
    """
    try:
        if not url.strip():
            return {
                "success": False,
                "error": "Article URL cannot be empty",
                "url": url
            }
        
        # Verify that URL is a valid AWS blog/news URL
        if not ("aws.amazon.com" in url.lower()):
            return {
                "success": False,
                "error": "This tool supports only AWS articles (aws.amazon.com)",
                "url": url
            }
        
        # Download article content
        content_result = await aws_news_api.fetch_article_content(url)
        
        return content_result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error downloading article content: {e}",
            "url": url
        }


def main():
    """Main function for running MCP server with SSE transport"""
    parser = argparse.ArgumentParser(description="AWS Blogs MCP Server - SSE Version")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8807, help="Port to bind to")
    
    args = parser.parse_args()
    
    print(f"AWS Blogs MCP Server (SSE) initialized", file=sys.stderr)
    print(f"Starting server on {args.host}:{args.port}", file=sys.stderr)
    print(f"API endpoint: https://api.aws-news.com/articles", file=sys.stderr)
    
    # Start MCP server with SSE transport
    mcp.run(transport="sse", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
