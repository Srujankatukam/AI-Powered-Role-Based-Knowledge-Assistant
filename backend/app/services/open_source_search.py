"""
Open-source web search service replacing paid APIs
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
import aiohttp
import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import quote_plus, urljoin, urlparse
import re

# DuckDuckGo search
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

# Newspaper for article extraction
try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False

from ..core.config import settings

logger = logging.getLogger(__name__)


class DuckDuckGoSearch:
    """DuckDuckGo search implementation"""
    
    def __init__(self, max_results: int = 5, timeout: int = 10):
        self.max_results = max_results
        self.timeout = timeout
        self.ddgs = DDGS() if DDGS_AVAILABLE else None
    
    async def search(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo"""
        if not self.ddgs:
            logger.warning("DuckDuckGo search not available")
            return []
        
        max_results = max_results or self.max_results
        
        try:
            # Run in thread pool since DDGS is synchronous
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, self._search_sync, query, max_results
            )
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {str(e)}")
            return []
    
    def _search_sync(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Synchronous search implementation"""
        try:
            results = []
            search_results = self.ddgs.text(query, max_results=max_results)
            
            for result in search_results:
                formatted_result = {
                    "title": result.get("title", "No title"),
                    "url": result.get("href", ""),
                    "content": result.get("body", "No content"),
                    "source": "duckduckgo"
                }
                results.append(formatted_result)
            
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo sync search error: {str(e)}")
            return []


class GoogleScraper:
    """Simple Google search scraper (use carefully to respect robots.txt)"""
    
    def __init__(self, max_results: int = 5, delay: float = 1.0):
        self.max_results = max_results
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    async def search(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search using Google (scraping)"""
        max_results = max_results or self.max_results
        
        try:
            # Run in thread pool
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, self._search_sync, query, max_results
            )
            return results
            
        except Exception as e:
            logger.error(f"Google search error: {str(e)}")
            return []
    
    def _search_sync(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Synchronous Google search"""
        try:
            # Add delay to be respectful
            time.sleep(self.delay)
            
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&num={max_results}"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Parse search results
            for g in soup.find_all('div', class_='g')[:max_results]:
                try:
                    # Extract title
                    title_elem = g.find('h3')
                    title = title_elem.get_text() if title_elem else "No title"
                    
                    # Extract URL
                    link_elem = g.find('a')
                    url = link_elem.get('href') if link_elem else ""
                    
                    # Extract snippet
                    snippet_elem = g.find('span', class_=['aCOpRe', 'hgKElc'])
                    if not snippet_elem:
                        snippet_elem = g.find('div', class_=['VwiC3b', 'yXK7lf'])
                    content = snippet_elem.get_text() if snippet_elem else "No content"
                    
                    if url and title:
                        results.append({
                            "title": title,
                            "url": url,
                            "content": content,
                            "source": "google"
                        })
                        
                except Exception as e:
                    logger.debug(f"Error parsing search result: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Google sync search error: {str(e)}")
            return []


class BingScraper:
    """Simple Bing search scraper"""
    
    def __init__(self, max_results: int = 5, delay: float = 1.0):
        self.max_results = max_results
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    async def search(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search using Bing"""
        max_results = max_results or self.max_results
        
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, self._search_sync, query, max_results
            )
            return results
            
        except Exception as e:
            logger.error(f"Bing search error: {str(e)}")
            return []
    
    def _search_sync(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Synchronous Bing search"""
        try:
            time.sleep(self.delay)
            
            search_url = f"https://www.bing.com/search?q={quote_plus(query)}&count={max_results}"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Parse Bing results
            for result in soup.find_all('li', class_='b_algo')[:max_results]:
                try:
                    # Extract title
                    title_elem = result.find('h2')
                    title = title_elem.get_text() if title_elem else "No title"
                    
                    # Extract URL
                    link_elem = result.find('a')
                    url = link_elem.get('href') if link_elem else ""
                    
                    # Extract snippet
                    snippet_elem = result.find('p')
                    content = snippet_elem.get_text() if snippet_elem else "No content"
                    
                    if url and title:
                        results.append({
                            "title": title,
                            "url": url,
                            "content": content,
                            "source": "bing"
                        })
                        
                except Exception as e:
                    logger.debug(f"Error parsing Bing result: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Bing sync search error: {str(e)}")
            return []


class ArticleExtractor:
    """Extract full article content from URLs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; KnowledgeBot/1.0)'
        })
    
    async def extract_article(self, url: str) -> Dict[str, Any]:
        """Extract article content from URL"""
        try:
            if NEWSPAPER_AVAILABLE:
                return await self._extract_with_newspaper(url)
            else:
                return await self._extract_with_requests(url)
                
        except Exception as e:
            logger.error(f"Article extraction error for {url}: {str(e)}")
            return {
                "title": "Extraction failed",
                "content": f"Could not extract content from {url}",
                "url": url
            }
    
    async def _extract_with_newspaper(self, url: str) -> Dict[str, Any]:
        """Extract using newspaper3k library"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._newspaper_sync, url)
    
    def _newspaper_sync(self, url: str) -> Dict[str, Any]:
        """Synchronous newspaper extraction"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            return {
                "title": article.title or "No title",
                "content": article.text or "No content extracted",
                "url": url,
                "authors": article.authors,
                "publish_date": str(article.publish_date) if article.publish_date else None
            }
            
        except Exception as e:
            logger.error(f"Newspaper extraction error: {str(e)}")
            return {
                "title": "Extraction failed",
                "content": f"Could not extract content: {str(e)}",
                "url": url
            }
    
    async def _extract_with_requests(self, url: str) -> Dict[str, Any]:
        """Simple extraction using requests and BeautifulSoup"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title_elem = soup.find('title')
            title = title_elem.get_text().strip() if title_elem else "No title"
            
            # Extract main content (simple heuristic)
            content_selectors = [
                'article', 'main', '.content', '.post-content', 
                '.entry-content', '.article-content', 'p'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = ' '.join([elem.get_text().strip() for elem in elements[:5]])
                    break
            
            return {
                "title": title,
                "content": content[:1000] + "..." if len(content) > 1000 else content,
                "url": url
            }
            
        except Exception as e:
            logger.error(f"Simple extraction error: {str(e)}")
            return {
                "title": "Extraction failed",
                "content": f"Could not extract content: {str(e)}",
                "url": url
            }


class OpenSourceSearchService:
    """Main open-source search service"""
    
    def __init__(self):
        self.ddg_search = DuckDuckGoSearch() if DDGS_AVAILABLE else None
        self.google_search = GoogleScraper()
        self.bing_search = BingScraper()
        self.article_extractor = ArticleExtractor()
        
        # Preferred search order
        self.search_engines = []
        if self.ddg_search:
            self.search_engines.append(("duckduckgo", self.ddg_search))
        self.search_engines.extend([
            ("bing", self.bing_search),
            ("google", self.google_search)
        ])
    
    async def search(
        self, 
        query: str, 
        max_results: int = 5,
        extract_content: bool = False,
        preferred_engine: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform web search using available engines
        
        Args:
            query: Search query
            max_results: Maximum number of results
            extract_content: Whether to extract full article content
            preferred_engine: Preferred search engine (duckduckgo, google, bing)
        """
        
        if not self.search_engines:
            return {
                "query": query,
                "results": [],
                "error": "No search engines available"
            }
        
        # Select search engine
        search_engine = None
        if preferred_engine:
            for name, engine in self.search_engines:
                if name == preferred_engine.lower():
                    search_engine = engine
                    break
        
        if not search_engine:
            # Use first available engine
            search_engine = self.search_engines[0][1]
            engine_name = self.search_engines[0][0]
        else:
            engine_name = preferred_engine.lower()
        
        try:
            # Perform search
            logger.info(f"Searching with {engine_name}: {query}")
            results = await search_engine.search(query, max_results)
            
            # Extract full content if requested
            if extract_content and results:
                enhanced_results = []
                for result in results:
                    if result.get("url"):
                        article_data = await self.article_extractor.extract_article(result["url"])
                        result["full_content"] = article_data.get("content", "")
                        result["extracted_title"] = article_data.get("title", "")
                    enhanced_results.append(result)
                results = enhanced_results
            
            return {
                "query": query,
                "results": results,
                "engine_used": engine_name,
                "total_results": len(results),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Search error with {engine_name}: {str(e)}")
            return {
                "query": query,
                "results": [],
                "error": str(e),
                "engine_used": engine_name,
                "status": "error"
            }
    
    async def multi_engine_search(
        self, 
        query: str, 
        max_results: int = 3
    ) -> Dict[str, Any]:
        """Search using multiple engines and combine results"""
        
        all_results = []
        engines_used = []
        
        # Search with all available engines
        tasks = []
        for engine_name, engine in self.search_engines[:2]:  # Limit to 2 engines
            tasks.append(self._search_with_engine(engine, engine_name, query, max_results))
        
        if tasks:
            engine_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in engine_results:
                if isinstance(result, dict) and result.get("results"):
                    all_results.extend(result["results"])
                    engines_used.append(result.get("engine_used", "unknown"))
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return {
            "query": query,
            "results": unique_results[:max_results * 2],  # Allow more results from multi-search
            "engines_used": engines_used,
            "total_results": len(unique_results),
            "status": "success"
        }
    
    async def _search_with_engine(
        self, 
        engine, 
        engine_name: str, 
        query: str, 
        max_results: int
    ) -> Dict[str, Any]:
        """Search with a specific engine"""
        try:
            results = await engine.search(query, max_results)
            return {
                "results": results,
                "engine_used": engine_name,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error with {engine_name}: {str(e)}")
            return {
                "results": [],
                "engine_used": engine_name,
                "status": "error",
                "error": str(e)
            }
    
    def get_available_engines(self) -> List[str]:
        """Get list of available search engines"""
        return [name for name, _ in self.search_engines]
    
    def is_available(self) -> bool:
        """Check if search service is available"""
        return len(self.search_engines) > 0


# Global search service instance
_search_service = None

def get_search_service() -> OpenSourceSearchService:
    """Get the global search service instance"""
    global _search_service
    
    if _search_service is None:
        _search_service = OpenSourceSearchService()
        logger.info(f"Initialized search service with engines: {_search_service.get_available_engines()}")
    
    return _search_service