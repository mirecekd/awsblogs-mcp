"""
Data processor for AWS News API

Processes data from https://api.aws-news.com/articles
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import aiohttp
from dateutil import parser as date_parser
from bs4 import BeautifulSoup
import re


class AWSNewsAPI:
    """Client for working with AWS News API"""
    
    BASE_URL = "https://api.aws-news.com/articles"
    
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, Any] = {}
        self._cache_timeout = 300  # 5 minutes cache
        self._last_fetch = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Gets or creates HTTP session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Closes HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def fetch_articles(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Downloads articles from AWS News API
        
        Args:
            limit: Maximum number of articles (None = all available)
            
        Returns:
            List of articles
        """
        # Check cache
        current_time = datetime.now()
        if (self._last_fetch and 
            (current_time - self._last_fetch).seconds < self._cache_timeout and
            'articles' in self._cache):
            articles = self._cache['articles']
        else:
            # Download new data
            session = await self._get_session()
            
            try:
                async with session.get(self.BASE_URL) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get('articles', [])
                        
                        # Save to cache
                        self._cache['articles'] = articles
                        self._last_fetch = current_time
                    else:
                        raise Exception(f"API error: {response.status}")
            except Exception as e:
                raise Exception(f"Error downloading data: {e}")
        
        # Apply limit
        if limit and limit > 0:
            articles = articles[:limit]
            
        return articles
    
    def filter_by_type(self, articles: List[Dict[str, Any]], article_type: str) -> List[Dict[str, Any]]:
        """
        Filters articles by type
        
        Args:
            articles: List of articles
            article_type: "News", "Blog", or "Both"
            
        Returns:
            Filtered articles
        """
        if article_type.lower() == "both":
            return articles
        
        return [
            article for article in articles 
            if article.get("type", "").lower() == article_type.lower()
        ]
    
    def filter_by_category(self, articles: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
        """
        Filters articles by main category
        
        Args:
            articles: List of articles
            category: Category name
            
        Returns:
            Filtered articles
        """
        return [
            article for article in articles 
            if article.get("main_category", "").lower() == category.lower()
        ]
    
    def filter_by_date_range(self, articles: List[Dict[str, Any]], 
                           from_date: Optional[str] = None, 
                           to_date: Optional[str] = None,
                           days_back: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Filters articles by date range
        
        Args:
            articles: List of articles
            from_date: From date (YYYY-MM-DD)
            to_date: To date (YYYY-MM-DD)
            days_back: Number of days back from today
            
        Returns:
            Filtered articles
        """
        if days_back:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
        filtered = []
        for article in articles:
            article_date_str = article.get("published_date", "")
            if not article_date_str:
                continue
                
            try:
                # Parse ISO 8601 datetime string
                article_date = date_parser.parse(article_date_str).date()
                
                # Check from_date
                if from_date:
                    from_dt = datetime.strptime(from_date, "%Y-%m-%d").date()
                    if article_date < from_dt:
                        continue
                
                # Check to_date
                if to_date:
                    to_dt = datetime.strptime(to_date, "%Y-%m-%d").date()
                    if article_date > to_dt:
                        continue
                
                filtered.append(article)
                
            except (ValueError, TypeError):
                # If unable to parse date, skip the article
                continue
        
        return filtered
    
    def filter_todays_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filters articles published today
        
        Args:
            articles: List of articles
            
        Returns:
            Today's articles
        """
        today = datetime.now().date()
        return self.filter_by_date_range(articles, from_date=today.strftime("%Y-%m-%d"))
    
    def search_articles(self, articles: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        Searches articles by text in title or URL
        
        Args:
            articles: List of articles
            query: Search query
            
        Returns:
            Found articles
        """
        query_lower = query.lower()
        
        return [
            article for article in articles
            if (query_lower in article.get("title", "").lower() or
                query_lower in article.get("url", "").lower() or
                query_lower in article.get("slug", "").lower())
        ]
    
    def get_available_categories(self, articles: List[Dict[str, Any]]) -> List[str]:
        """
        Gets list of available categories
        
        Args:
            articles: List of articles
            
        Returns:
            List of unique categories
        """
        categories = set()
        for article in articles:
            category = article.get("main_category")
            if category:
                categories.add(category)
        
        return sorted(list(categories))
    
    async def fetch_article_content(self, url: str) -> Dict[str, Any]:
        """
        Downloads full article content from a given URL
        
        Args:
            url: Article URL
            
        Returns:
            Dict with article content
        """
        session = await self._get_session()
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html_content = await response.text()
                    
                    # Parse HTML using BeautifulSoup
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Extract title
                    title = ""
                    title_tag = soup.find('h1') or soup.find('title')
                    if title_tag:
                        title = title_tag.get_text().strip()
                    
                    # Extract main content
                    content = ""
                    
                    # Try to find main article content
                    # AWS blogs usually use these selectors
                    content_selectors = [
                        'div.blog-post-content',
                        'div.entry-content', 
                        'article.post-content',
                        'div.content',
                        'main',
                        '.blog-post-body',
                        '.post-body'
                    ]
                    
                    content_element = None
                    for selector in content_selectors:
                        content_element = soup.select_one(selector)
                        if content_element:
                            break
                    
                    # If we don't find specific selector, take all p tags
                    if not content_element:
                        paragraphs = soup.find_all('p')
                        if paragraphs:
                            content = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    else:
                        # Clean content from unnecessary tags
                        # Remove scripts, styles, navigation, etc.
                        for unwanted in content_element(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                            unwanted.decompose()
                        
                        # Get clean text
                        content = content_element.get_text()
                        
                        # Clean excessive whitespace
                        content = re.sub(r'\n\s*\n', '\n\n', content)
                        content = re.sub(r' +', ' ', content)
                        content = content.strip()
                    
                    # Extract meta information
                    meta_description = ""
                    meta_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
                    if meta_tag:
                        meta_description = meta_tag.get('content', '').strip()
                    
                    # Extract author
                    author = ""
                    author_selectors = [
                        'meta[name="author"]',
                        '.author',
                        '.byline', 
                        '.post-author'
                    ]
                    
                    for selector in author_selectors:
                        author_element = soup.select_one(selector)
                        if author_element:
                            if author_element.name == 'meta':
                                author = author_element.get('content', '').strip()
                            else:
                                author = author_element.get_text().strip()
                            break
                    
                    # Extract publication date from HTML
                    pub_date = ""
                    date_selectors = [
                        'time[datetime]',
                        'meta[property="article:published_time"]',
                        '.publish-date',
                        '.date'
                    ]
                    
                    for selector in date_selectors:
                        date_element = soup.select_one(selector)
                        if date_element:
                            if date_element.name == 'time':
                                pub_date = date_element.get('datetime', '').strip()
                            elif date_element.name == 'meta':
                                pub_date = date_element.get('content', '').strip()
                            else:
                                pub_date = date_element.get_text().strip()
                            break
                    
                    return {
                        "success": True,
                        "url": url,
                        "title": title,
                        "content": content,
                        "description": meta_description,
                        "author": author,
                        "published_date": pub_date,
                        "content_length": len(content),
                        "word_count": len(content.split()) if content else 0
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP error {response.status} when downloading article",
                        "url": url
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Error downloading article: {e}",
                "url": url
            }
    
    def format_article_response(self, articles: List[Dict[str, Any]], 
                              filters_applied: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Formats response with articles
        
        Args:
            articles: List of articles
            filters_applied: Applied filters
            
        Returns:
            Structured response
        """
        formatted_articles = []
        
        for article in articles:
            # Parse date for better display
            published_date = article.get("published_date", "")
            formatted_date = ""
            if published_date:
                try:
                    dt = date_parser.parse(published_date)
                    formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    formatted_date = published_date
            
            formatted_article = {
                "id": article.get("id", ""),
                "title": article.get("title", ""),
                "type": article.get("type", ""),
                "category": article.get("main_category", ""),
                "published_date": formatted_date,
                "url": article.get("url", ""),
                "slug": article.get("slug", ""),
                "is_popular": article.get("popular", False),
                "is_regional_expansion": article.get("is_regional_expansion", False)
            }
            formatted_articles.append(formatted_article)
        
        return {
            "success": True,
            "articles": formatted_articles,
            "total_count": len(formatted_articles),
            "filters_applied": filters_applied or {}
        }


# Global API client instance
aws_news_api = AWSNewsAPI()
