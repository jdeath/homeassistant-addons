#!/usr/bin/env python3
"""
MCP Server: Category-aware web search, website scraping, and date/time tools.
"""

import asyncio
import json
import logging
import os
import pathlib
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone, timedelta
from typing import Callable, Any, Dict, Optional, Awaitable, List, Union, TypeVar, Type
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, validator, ValidationError, root_validator
import trafilatura
from dateutil import parser as date_parser
from cachetools import TTLCache
from zoneinfo import ZoneInfo
import filetype
import pymupdf
import pymupdf4llm
from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# --- Custom Exceptions ---
class MCPServerError(Exception):
    """Base exception class for MCP Server errors."""
    pass

class ConfigurationError(MCPServerError):
    """Raised when there's an issue with configuration values."""
    pass

class SearXNGConnectionError(MCPServerError):
    """Raised when connection to SearXNG fails."""
    pass

class WebScrapingError(MCPServerError):
    """Raised when web scraping fails."""
    pass

class RateLimitExceededError(MCPServerError):
    """Raised when rate limit for a domain is exceeded."""
    pass

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# --- Global Cache ---
website_cache = None

# --- Rate Limiting and Cache Validation ---
class RateLimiter:
    """Implements domain-based rate limiting for web requests."""
    
    def __init__(self, requests_per_minute: int = 10, timeout_seconds: int = 60):
        """
        Initialize the rate limiter.
        
        Args:
            requests_per_minute: Maximum number of requests allowed per domain per minute
            timeout_seconds: How long to track requests for each domain
        """
        self.requests_per_minute = requests_per_minute
        self.timeout_seconds = timeout_seconds
        self.domain_requests = {}  # Maps domain to list of request timestamps
        
    def can_request(self, url: str) -> bool:
        """
        Check if a request to the given URL is allowed under rate limits.
        
        Args:
            url: The URL to check
            
        Returns:
            True if the request is allowed, False otherwise
        """
        domain = urlparse(url).netloc
        if not domain:
            return True  # No domain, allow request
            
        current_time = time.time()
        
        # Initialize domain entry if not exists
        if domain not in self.domain_requests:
            self.domain_requests[domain] = []
            
        # Clean up old requests
        self.domain_requests[domain] = [
            timestamp for timestamp in self.domain_requests[domain]
            if current_time - timestamp < self.timeout_seconds
        ]
        
        # Check if we're over the limit
        if len(self.domain_requests[domain]) >= self.requests_per_minute:
            return False
            
        # Add current request timestamp
        self.domain_requests[domain].append(current_time)
        return True
        
    def get_remaining_time(self, url: str) -> float:
        """
        Get the remaining time in seconds before a request can be made.
        
        Args:
            url: The URL to check
            
        Returns:
            Time in seconds to wait, or 0 if request can be made immediately
        """
        domain = urlparse(url).netloc
        if not domain or domain not in self.domain_requests:
            return 0
            
        current_time = time.time()
        timestamps = self.domain_requests[domain]
        
        # Clean up old requests
        timestamps = [t for t in timestamps if current_time - t < self.timeout_seconds]
        
        if len(timestamps) < self.requests_per_minute:
            return 0
            
        # Find oldest timestamp and calculate when it will expire
        oldest = min(timestamps)
        return max(0, oldest + self.timeout_seconds - current_time)


class CacheValidator:
    """Handles validation of cached web content."""
    
    @staticmethod
    def is_valid(cached_result: Dict[str, Any], max_age_minutes: int = 30) -> bool:
        """
        Check if a cached result is still valid.
        
        Args:
            cached_result: The cached result to validate
            max_age_minutes: Maximum age in minutes for cached content to be considered valid
            
        Returns:
            True if the cached result is valid, False otherwise
        """
        if not cached_result:
            return False
            
        # Check if the cached result has an access timestamp
        if "date_accessed" not in cached_result:
            return False
            
        try:
            # Parse the date_accessed timestamp
            date_accessed = date_parser.parse(cached_result["date_accessed"])
            
            # Check if the cache entry is too old
            now = datetime.now(timezone.utc)
            age_td = now - date_accessed
            return age_td.total_seconds() < (max_age_minutes * 60)
        except (ValueError, TypeError):
            return False

# --- Helper Functions ---
class HelperFunctions:
    @staticmethod
    def get_base_url(url: str) -> str:
        parsed_url = urlparse(url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}"

    @staticmethod
    def generate_excerpt(content: str, max_length: int = 200) -> str:
        lines = content.splitlines()
        excerpt = ""
        for line in lines:
            if len(excerpt) + len(line) + 1 < max_length:
                excerpt += line + "\n"
            else:
                remaining_len = max_length - len(excerpt) - 4
                if remaining_len > 0:
                    excerpt += line[:remaining_len] + " ..."
                break
        return excerpt.strip() if excerpt else content[:max_length] + "..."

    @staticmethod
    def format_text_with_trafilatura(html_content: str, timeout: int) -> str:
        extracted_text = trafilatura.extract(
            html_content,
            favor_readability=True,
            include_comments=False,
            include_tables=True,
            timeout=timeout
        )
        if not extracted_text:
            soup = BeautifulSoup(html_content, "html.parser")
            extracted_text = soup.get_text(separator="\n", strip=True)
            logger.warning("Trafilatura failed/timed out, falling back to basic text extraction.")
        lines = [unicodedata.normalize("NFKC", line).strip() for line in extracted_text.splitlines()]
        cleaned_lines = [re.sub(r'\s{2,}', ' ', line) for line in lines if line]
        formatted_text = "\n".join(cleaned_lines)
        return HelperFunctions.remove_emojis(formatted_text).strip()

    @staticmethod
    def remove_emojis(text: str) -> str:
        return "".join(c for c in text if not unicodedata.category(c).startswith("So"))

    @staticmethod
    def truncate_to_n_words(text: str, word_limit: int) -> str:
        tokens = text.split()
        if len(tokens) <= word_limit:
            return text
        return " ".join(tokens[:word_limit]) + "..."

    @staticmethod
    def _modify_reddit_url(url: str) -> str:
        match = re.match(r"^(https?://)(www\.)?(reddit\.com)(.*)$", url, re.IGNORECASE)
        if match:
            protocol = match.group(1)
            path_and_query = match.group(4)
            return f"{protocol}old.reddit.com{path_and_query}"
        return url

    @staticmethod
    async def process_web_search_result(result: Dict[str, Any], valves, client) -> Dict[str, Any]:
        """Process a web search result to extract content and metadata."""
        url = result.get("url")
        if not url:
            return None
        
        # Check for ignored websites
        if valves.IGNORED_WEBSITES:
            ignored_sites = [site.strip() for site in valves.IGNORED_WEBSITES.split(",")]
            if any(site in url for site in ignored_sites):
                return {"url": url, "title": result.get("title", ""), "error": "Ignored website", "soup": None}
        
        # Try to get content from the website
        try:
            url_to_fetch = HelperFunctions._modify_reddit_url(url)
            response = await client.get(url_to_fetch, timeout=valves.SCRAPING_TIMEOUT)
            response.raise_for_status()
            html_content = response.text
            raw_content = response.content

            # We only need a couple of initial bytes, not the whole file for MIME type guess
            kind = filetype.guess(raw_content)

            if kind is not None and kind.mime == "application/pdf":
                # Process PDF
                doc = pymupdf.open(stream=raw_content, filetype="pdf")
                md_text = pymupdf4llm.to_markdown(doc)
    
                content = md_text
                truncated_content = HelperFunctions.truncate_to_n_words(content, valves.PAGE_CONTENT_WORDS_LIMIT)
                excerpt = HelperFunctions.generate_excerpt(content)

                title = "A PDF document converted to Markdown"
                soup = None
            else:
                # Assume HTML for now
                soup = BeautifulSoup(html_content, "html.parser")
                title = result.get("title") or (soup.title.string if soup.title else "No title")
                title = unicodedata.normalize("NFKC", title.strip())
                title = HelperFunctions.remove_emojis(title)
            
                content = HelperFunctions.format_text_with_trafilatura(html_content, valves.TRAFILATURA_TIMEOUT)
                truncated_content = HelperFunctions.truncate_to_n_words(content, valves.PAGE_CONTENT_WORDS_LIMIT)
                excerpt = HelperFunctions.generate_excerpt(content)
            
            return {
                "title": title,
                "url": url,
                "content": truncated_content,
                "excerpt": excerpt,
                "snippet": result.get("content", ""),
                "date_accessed": datetime.now(timezone.utc).isoformat(),
                "soup": soup,
                "error": None
            }
        except httpx.HTTPStatusError as e:
            error_msg = f"{e.response.status_code} {e.response.reason_phrase}"
            return {
                "title": result.get("title", ""),
                "url": url,
                "snippet": result.get("content", ""),
                "error": error_msg,
                "soup": None
            }
        except httpx.RequestError as e:
            error_msg = f"Request failed: {str(e)}"
            return {
                "title": result.get("title", ""),
                "url": url,
                "snippet": result.get("content", ""),
                "error": error_msg,
                "soup": None
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            return {
                "title": result.get("title", ""),
                "url": url,
                "snippet": result.get("content", ""),
                "error": error_msg,
                "soup": None
            }

# --- Event Emitter ---
class MCPEventEmitter:
    def __init__(self, send_notification_func: Callable[[str, Any], Awaitable[None]]):
        self.send_notification_func = send_notification_func

    async def emit(self, description: str = "Unknown State", status: str = "in_progress", done: bool = False, step_number: Optional[float] = None):
        message_data = {"status": status, "description": description, "done": done}
        if step_number is not None:
            message_data["step"] = step_number
        await self.send_notification_func("tool/event", {"type": "status", "data": message_data})

    async def emit_citation(self, soup: Optional[BeautifulSoup], result_data: Dict[str, Any]):
        pub_date_str = None
        author_str = None
        if soup:
            date_selectors = [
                {'property': 'article:published_time'}, {'name': 'datePublished'}, {'itemprop': 'datePublished'},
                {'name': 'pubdate'}, {'name': 'creation_date'}, {'name': 'date'}, {'name': 'dcterms.date'}, {'name': 'DC.date.issued'}
            ]
            for selector in date_selectors:
                tag = soup.find('meta', selector)
                if tag and tag.get('content'):
                    try:
                        parsed_date = date_parser.parse(tag['content'])
                        pub_date_str = parsed_date.strftime('%Y-%m-%d')
                        break
                    except (ValueError, OverflowError, TypeError):
                        pass
            author_selectors = [{'name': 'author'}, {'property': 'article:author'}, {'name': 'creator'}, {'name': 'DC.creator'}]
            for selector in author_selectors:
                tag = soup.find('meta', selector)
                if tag and tag.get('content'):
                    author_str = tag['content'].strip()
                    break
        doc_content = result_data.get("content") or result_data.get("snippet") or result_data.get("title", "")
        metadata = {"source": result_data["url"], "date_accessed": datetime.now(timezone.utc).isoformat(), "title": result_data["title"]}
        if pub_date_str:
            metadata["date_published"] = pub_date_str
        if author_str:
            metadata["author"] = author_str
        source_info = {"name": result_data["title"], "url": result_data["url"]}
        if result_data.get("is_image_result"):
            source_info["type"] = "image"
        elif result_data.get("is_video_result"):
            source_info["type"] = "video"
        elif result_data.get("is_file_result"):
            source_info["type"] = "file"
        elif result_data.get("is_map_result"):
            source_info["type"] = "map"
        elif result_data.get("is_social_result"):
            source_info["type"] = "social_media_post"
        elif "excerpt" in result_data:
            source_info["type"] = "webpage"
        citation_data = {"document": [doc_content], "metadata": [metadata], "source": source_info}
        await self.send_notification_func("tool/event", {"type": "citation", "data": citation_data})

# --- Configuration Management ---
class Tools:
    class Valves(BaseModel):
        SEARXNG_ENGINE_API_BASE_URL: str = Field(default="http://host.docker.internal:8080/search")
        IGNORED_WEBSITES: str = Field(default="")
        RETURNED_SCRAPPED_PAGES_NO: int = Field(default=3, ge=1, le=20)
        SCRAPPED_PAGES_NO: int = Field(default=5, ge=1, le=30)
        PAGE_CONTENT_WORDS_LIMIT: int = Field(default=5000, ge=50, le=20000)
        CITATION_LINKS: bool = Field(default=True)
        desired_timezone: str = Field(default="America/New_York")
        TRAFILATURA_TIMEOUT: int = Field(default=15, ge=5, le=60)
        MAX_IMAGE_RESULTS: int = Field(default=10, ge=1, le=50)
        MAX_VIDEO_RESULTS: int = Field(default=10, ge=1, le=50)
        MAX_FILE_RESULTS: int = Field(default=5, ge=1, le=20)
        MAX_MAP_RESULTS: int = Field(default=5, ge=1, le=20)
        MAX_SOCIAL_RESULTS: int = Field(default=5, ge=1, le=20)
        SCRAPING_TIMEOUT: int = Field(default=20, ge=5, le=120)
        CACHE_MAXSIZE: int = Field(default=100, ge=10, le=1000)
        CACHE_TTL_MINUTES: int = Field(default=5, ge=1, le=1440)
        RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=10, ge=1, le=60)
        RATE_LIMIT_TIMEOUT_SECONDS: int = Field(default=60, ge=10, le=3600)
        CACHE_MAX_AGE_MINUTES: int = Field(default=30, ge=1, le=1440)
        MCP_HTTP_HOST: str = Field(default="0.0.0.0")
        MCP_HTTP_PORT: str = Field(default="8080")
        
        @validator('SEARXNG_ENGINE_API_BASE_URL')
        def validate_searxng_url(cls, v):
            if not v.startswith(('http://', 'https://')):
                raise ConfigurationError(f"SEARXNG_ENGINE_API_BASE_URL must start with http:// or https://, got {v}")
            return v
            
        @validator('desired_timezone')
        def validate_timezone(cls, v):
            try:
                ZoneInfo(v)
                return v
            except Exception as e:
                raise ConfigurationError(f"Invalid timezone: {v}. Error: {str(e)}. See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for a list of valid timezones.")
                
        @root_validator(pre=True)
        def check_page_limits(cls, values):
            if 'SCRAPPED_PAGES_NO' in values and 'RETURNED_SCRAPPED_PAGES_NO' in values:
                if values['SCRAPPED_PAGES_NO'] < values['RETURNED_SCRAPPED_PAGES_NO']:
                    raise ConfigurationError(
                        f"SCRAPPED_PAGES_NO ({values['SCRAPPED_PAGES_NO']}) must be greater than or equal to "
                        f"RETURNED_SCRAPPED_PAGES_NO ({values['RETURNED_SCRAPPED_PAGES_NO']})"
                    )
            return values

    @staticmethod
    def load_config_file(config_path: str) -> dict:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def save_config_file(config_path: str, config: dict):
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def __init__(self, send_notification_func: Optional[Callable[[str, Any], Awaitable[None]]] = None):
        """
        Initialize the Tools class with configuration from script defaults, config file, and environment variables.
        Configuration is loaded in the following priority order:
        1. Script defaults (lowest priority)
        2. Config file (middle priority)
        3. Environment variables (highest priority)
        
        The config file is only written if:
        - It doesn't exist yet (first-time initialization)
        - Environment variables are explicitly provided for this run
        """
        if send_notification_func is None:
            async def _noop(method: str, params: Any) -> None:
                pass
            send_notification_func = _noop

        # 1. Load defaults from script
        script_defaults = self.Valves().dict()
        
        # 2. Try to load config file (default: /config/ods_config.json, fallback: ./ods_config.json)
        config_path = os.getenv("ODS_CONFIG_PATH", "/config/ods_config.json")
        #if not pathlib.Path(config_path).exists():
        #    config_path = "./ods_config.json"
        
        file_exists = pathlib.Path(config_path).exists()
        file_config = self.load_config_file(config_path)
        
        # 3. Load from env vars
        env_vars_present = False
        env_config = {}
        
        # Special handling for DESIRED_TIMEZONE which has different casing in the model
        desired_tz = os.getenv("DESIRED_TIMEZONE")
        if desired_tz is not None:
            env_vars_present = True
            env_config["desired_timezone"] = desired_tz
        
        for k in script_defaults.keys():
            # Skip desired_timezone as it's handled separately
            if k == "desired_timezone":
                continue
                
            env_value = os.getenv(k.upper(), None)
            if env_value is not None:
                env_vars_present = True
                default_type = type(script_defaults[k])
                try:
                    if default_type is bool:
                        env_config[k] = env_value.lower() == "true"
                    else:
                        env_config[k] = default_type(env_value)
                except Exception:
                    logger.warning(f"Invalid environment variable value for {k.upper()}: {env_value}")
                    env_config[k] = script_defaults[k]
        
        # 4. Merge: script_defaults < file_config < env_config
        merged = {**script_defaults, **(file_config or {}), **env_config}
        self.valves = self.Valves(**merged)
        
        # 5. Save config file ONLY in these cases:
        # - If the file doesn't exist yet (first-time initialization)
        # - If environment variables were provided for this run
        if (not file_exists or env_vars_present):
            logger.info(f"Saving configuration to {config_path} (reason: {'first run' if not file_exists else 'env vars provided'})")
            self.save_config_file(config_path, merged)
        
        logger.info(f"Initializing with timezone: {self.valves.desired_timezone}")
        global website_cache
        website_cache = TTLCache(
            maxsize=self.valves.CACHE_MAXSIZE,
            ttl=timedelta(minutes=self.valves.CACHE_TTL_MINUTES).total_seconds()
        )
        logger.info(f"Website cache initialized: maxsize={self.valves.CACHE_MAXSIZE}, ttl={self.valves.CACHE_TTL_MINUTES} minutes")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.functions = HelperFunctions()
        self.emitter = MCPEventEmitter(send_notification_func)
        self.client = httpx.AsyncClient(headers=self.headers, follow_redirects=True)

    # --- Tool Methods ---
    async def search_web(self, query: str, engines: Optional[str] = None, category: Optional[str] = "general", safesearch: Optional[str] = None, time_range: Optional[str] = None) -> str:
        safe_category = category.lower().strip() if category else "general"
        search_type = safe_category if safe_category != "general" else "web"
        await self.emitter.emit(f"🔍 Starting {search_type} search", step_number=1)
        await self.emitter.emit(f"📝 Searching for query: {query}", step_number=2)
        params = {"q": query, "format": "json", "pageno": 1}
        if engines:
            params["engines"] = engines
        params["categories"] = safe_category
        if safesearch and safesearch in ["0", "1", "2"]:
            params["safesearch"] = safesearch
        if time_range and time_range in ["day", "month", "year"]:
            params["time_range"] = time_range
        processed_results = []
        try:
            await self.emitter.emit(f"🌐 Connecting to SearXNG at {self.valves.SEARXNG_ENGINE_API_BASE_URL}", step_number=4)
            resp = await self.client.get(self.valves.SEARXNG_ENGINE_API_BASE_URL, params=params, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            await self.emitter.emit(f"📊 {len(results)} raw results found for category '{safe_category}'", step_number=5)
        except httpx.HTTPStatusError as e:
            error_msg = f"SearXNG search failed: {e.response.status_code} {e.response.reason_phrase}"
            await self.emitter.emit(status="error", description=f"❌ {error_msg}", done=True)
            raise SearXNGConnectionError(error_msg) from e
        except httpx.RequestError as e:
            error_msg = f"Error connecting to SearXNG: {str(e)}"
            await self.emitter.emit(status="error", description=f"❌ {error_msg}", done=True)
            raise SearXNGConnectionError(error_msg) from e
        except json.JSONDecodeError as e:
            error_msg = f"Error decoding SearXNG response: {str(e)}"
            await self.emitter.emit(status="error", description=f"❌ {error_msg}", done=True)
            raise SearXNGConnectionError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during search: {str(e)}"
            await self.emitter.emit(status="error", description=f"❌ {error_msg}", done=True)
            raise MCPServerError(error_msg) from e
            
        if not results:
            await self.emitter.emit(status="complete", description="✅ Search complete - No results found.", done=True, step_number=6)
            return "No results found."
            
        output_parts = []
        final_results_count = 0
        category_limit = {
            "images": self.valves.MAX_IMAGE_RESULTS,
            "videos": self.valves.MAX_VIDEO_RESULTS,
            "files": self.valves.MAX_FILE_RESULTS,
            "map": self.valves.MAX_MAP_RESULTS,
            "social media": self.valves.MAX_SOCIAL_RESULTS,
        }.get(safe_category, self.valves.RETURNED_SCRAPPED_PAGES_NO)
        
        # Rate limiter for scraping operations
        rate_limiter = RateLimiter(
            requests_per_minute=self.valves.RATE_LIMIT_REQUESTS_PER_MINUTE,
            timeout_seconds=self.valves.RATE_LIMIT_TIMEOUT_SECONDS
        )
        
        if safe_category == "images":
            await self.emitter.emit("🖼️ Processing image results", step_number=6)
            for i, result in enumerate(results[:category_limit]):
                if i > 0:
                    output_parts.append("\n====================\n")
                img_data = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "img_src": result.get("img_src", ""),
                    "is_image_result": True
                }
                output_parts.append(f"**Title:** {img_data['title'] or 'N/A'}")
                output_parts.append(f"**Image URL:** {img_data['img_src'] or 'N/A'}")
                output_parts.append(f"**Source Page:** {img_data['url'] or 'N/A'}")
                if img_data['img_src']:
                    output_parts.append(f"\n![{img_data['title'] or 'Image'}]({img_data['img_src']})")
                processed_results.append(img_data)
                if self.valves.CITATION_LINKS:
                    citation_content = f"Image source: {img_data['url']}"
                    await self.emitter.emit_citation(None, {"content": citation_content, **img_data})
            final_results_count = len(processed_results)
            await self.emitter.emit(status="complete", description=f"✅ Image search complete - {final_results_count} images returned.", done=True, step_number=7)
        elif safe_category == "videos":
            await self.emitter.emit("🎬 Processing video results", step_number=6)
            for i, result in enumerate(results[:category_limit]):
                if i > 0:
                    output_parts.append("\n====================\n")
                vid_data = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "source": result.get("source", ""),
                    "iframe_src": result.get("iframe_src", ""),
                    "is_video_result": True
                }
                output_parts.append(f"**Title:** {vid_data['title'] or 'N/A'}")
                output_parts.append(f"**URL:** {vid_data['url'] or 'N/A'}")
                if vid_data.get('source'):
                    output_parts.append(f"**Source:** {vid_data['source']}")
                if vid_data.get('iframe_src'):
                    output_parts.append(f"**Embed URL:** {vid_data['iframe_src']}")
                if vid_data.get('content'):
                    output_parts.append(f"\n**Description:**\n{vid_data['content']}")
                processed_results.append(vid_data)
                if self.valves.CITATION_LINKS:
                    await self.emitter.emit_citation(None, vid_data)
            final_results_count = len(processed_results)
            await self.emitter.emit(status="complete", description=f"✅ Video search complete - {final_results_count} videos returned.", done=True, step_number=7)
        elif safe_category == "files":
            await self.emitter.emit("📁 Processing file results", step_number=6)
            for i, result in enumerate(results[:category_limit]):
                if i > 0:
                    output_parts.append("\n====================\n")
                file_data = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "size": result.get("size", ""),
                    "format": result.get("format", ""),
                    "is_file_result": True
                }
                output_parts.append(f"**Title:** {file_data['title'] or 'N/A'}")
                output_parts.append(f"**URL:** {file_data['url'] or 'N/A'}")
                if file_data.get('format'):
                    output_parts.append(f"**Format:** {file_data['format']}")
                if file_data.get('size'):
                    output_parts.append(f"**Size:** {file_data['size']}")
                if file_data.get('content'):
                    output_parts.append(f"\n**Snippet:**\n{file_data['content']}")
                processed_results.append(file_data)
                if self.valves.CITATION_LINKS:
                    await self.emitter.emit_citation(None, file_data)
            final_results_count = len(processed_results)
            await self.emitter.emit(status="complete", description=f"✅ File search complete - {final_results_count} files returned.", done=True, step_number=7)
        elif safe_category == "map":
            await self.emitter.emit("🗺️ Processing map results", step_number=6)
            limit = self.valves.MAX_MAP_RESULTS
            for i, result in enumerate(results[:limit]):
                if i > 0:
                    output_parts.append("\n====================\n")
                map_data = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "address": result.get("address", ""),
                    "latitude": result.get("latitude"),
                    "longitude": result.get("longitude"),
                    "content": result.get("content", ""),
                    "is_map_result": True
                }
                output_parts.append(f"**Title:** {map_data['title'] or 'N/A'}")
                output_parts.append(f"**Map URL:** {map_data['url'] or 'N/A'}")
                if map_data.get('address'):
                    output_parts.append(f"**Address:** {map_data['address']}")
                if map_data.get('latitude') and map_data.get('longitude'):
                    output_parts.append(f"**Coordinates:** {map_data['latitude']}, {map_data['longitude']}")
                if map_data.get('content'):
                    output_parts.append(f"\n**Description:**\n{map_data.get('content')}")
                processed_results.append(map_data)
                if self.valves.CITATION_LINKS:
                    await self.emitter.emit_citation(None, map_data)
            final_results_count = len(processed_results)
            await self.emitter.emit(status="complete", description=f"✅ Map search complete - {final_results_count} locations returned.", done=True, step_number=7)
        elif safe_category == "social media":
            await self.emitter.emit("📱 Processing social media results", step_number=6)
            limit = self.valves.MAX_SOCIAL_RESULTS
            for i, result in enumerate(results[:limit]):
                if i > 0:
                    output_parts.append("\n====================\n")
                social_data = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "is_social_result": True
                }
                output_parts.append(f"**Title:** {social_data['title'] or 'N/A'}")
                output_parts.append(f"**URL:** {social_data['url'] or 'N/A'}")
                if social_data.get('content'):
                    output_parts.append(f"\n**Content:**\n{social_data['content']}")
                processed_results.append(social_data)
                if self.valves.CITATION_LINKS:
                    await self.emitter.emit_citation(None, social_data)
            final_results_count = len(processed_results)
            await self.emitter.emit(status="complete", description=f"✅ Social media search complete - {final_results_count} posts/profiles returned.", done=True, step_number=7)
        else:
            await self.emitter.emit("🔄 Processing web results by scraping pages", step_number=6)
            limited_results_for_scraping = results[:self.valves.SCRAPPED_PAGES_NO]
            tasks = []
            
            # Apply rate limiting to scraping operations
            for result in limited_results_for_scraping:
                url = result.get("url", "")
                if url:
                    # Check rate limits before adding task
                    if not rate_limiter.can_request(url):
                        domain = urlparse(url).netloc
                        wait_time = rate_limiter.get_remaining_time(url)
                        logger.warning(f"Rate limit exceeded for {domain}. Skipping result. Try again in {wait_time:.1f} seconds.")
                        continue
                
                tasks.append(HelperFunctions.process_web_search_result(result, self.valves, self.client))
                
            processed_results_with_soup = await asyncio.gather(*tasks)
            processed_count = 0
            for result_data in processed_results_with_soup:
                if result_data:
                    soup_obj = result_data.pop("soup", None)
                    processed_results.append(result_data)
                    if not result_data.get("error"):
                        processed_count += 1
                        await self.emitter.emit(f"📄 Scraped page {processed_count}/{len(tasks)}: {result_data.get('url', 'N/A')}", step_number=7)
                        if self.valves.CITATION_LINKS:
                            await self.emitter.emit_citation(soup_obj, result_data)
                if len([r for r in processed_results if not r.get("error")]) >= self.valves.RETURNED_SCRAPPED_PAGES_NO:
                    break
            processed_results = [res for res in processed_results if res]
            processed_results = processed_results[:self.valves.RETURNED_SCRAPPED_PAGES_NO]
            final_results_count = len(processed_results)
            await self.emitter.emit(status="complete", description=f"✅ Web search complete - {final_results_count} pages processed and returned.", done=True, step_number=8)
            for i, res in enumerate(processed_results):
                if i > 0:
                    output_parts.append("\n====================\n")
                output_parts.append(f"**Title:** {res.get('title', 'N/A')}")
                output_parts.append(f"**URL:** {res.get('url', 'N/A')}")
                if res.get("error"):
                    output_parts.append(f"**Error:** {res.get('error')}")
                else:
                    if 'snippet' in res and res.get('snippet'):
                        output_parts.append(f"\n**Snippet:** {res.get('snippet')}")
                    output_parts.append("\n\n**Content:**") # Added extra \n for spacing
                    output_parts.append(res.get('content', ''))
        return "\n".join(output_parts)

    async def _get_website_content_cached(self, url: str) -> Dict[str, Any]:
        soup = None
        html_content = ""
        try:
            url_to_fetch = HelperFunctions._modify_reddit_url(url)
            response_site = await self.client.get(url_to_fetch, timeout=120)
            response_site.raise_for_status()
            html_content = response_site.text

            #TODO: Refactor this into a separate function in order no to duplicate code used in search_web
            raw_content = response_site.content

            # We only need a couple of initial bytes, not the whole file for MIME type guess
            kind = filetype.guess(raw_content)

            if kind is not None and kind.mime == "application/pdf":
                # Process PDF
                doc = pymupdf.open(stream=raw_content, filetype="pdf")
                md_text = pymupdf4llm.to_markdown(doc)
    
                content_site = md_text
                truncated_content = HelperFunctions.truncate_to_n_words(content_site, self.valves.PAGE_CONTENT_WORDS_LIMIT)
                excerpt = HelperFunctions.generate_excerpt(content_site)

                page_title = "A PDF document converted to Markdown"
                soup = None
            else:
                soup = BeautifulSoup(html_content, "html.parser")
                page_title_tag = soup.find('title')
                page_title = page_title_tag.string if page_title_tag else "No title found"
                page_title = unicodedata.normalize("NFKC", page_title.strip())
                page_title = HelperFunctions.remove_emojis(page_title)
                content_site = HelperFunctions.format_text_with_trafilatura(html_content, self.valves.TRAFILATURA_TIMEOUT)
                truncated_content = HelperFunctions.truncate_to_n_words(content_site, self.valves.PAGE_CONTENT_WORDS_LIMIT)
                excerpt = HelperFunctions.generate_excerpt(content_site)

            return {
                "title": page_title, "url": url, "content": truncated_content,
                "excerpt": excerpt, "date_accessed": datetime.now(timezone.utc).isoformat(),
                "soup": soup, "error": None
            }
        except httpx.HTTPStatusError as e:
            error_msg = f"{e.response.status_code} {e.response.reason_phrase}"
            return {"url": url, "error": error_msg, "date_accessed": datetime.now(timezone.utc).isoformat(), "soup": None}
        except httpx.RequestError as e:
            error_msg = f"Request failed: {str(e)}"
            return {"url": url, "error": error_msg, "date_accessed": datetime.now(timezone.utc).isoformat(), "soup": None}
        except Exception as e:
            error_msg = f"Unexpected error processing website: {str(e)}"
            return {"url": url, "error": error_msg, "date_accessed": datetime.now(timezone.utc).isoformat(), "soup": None}

    async def get_website(self, url: str) -> str:
        parsed_url_input = urlparse(url)
        if not parsed_url_input.scheme:
            url = "https://" + url
            logger.info(f"URL '{url}' was missing a scheme. Prepended https://.")
            
        # Check rate limiting
        rate_limiter = RateLimiter(
            requests_per_minute=self.valves.RATE_LIMIT_REQUESTS_PER_MINUTE,
            timeout_seconds=self.valves.RATE_LIMIT_TIMEOUT_SECONDS
        )
        
        if not rate_limiter.can_request(url):
            wait_time = rate_limiter.get_remaining_time(url)
            error_msg = f"Rate limit exceeded for domain {parsed_url_input.netloc}. Try again in {wait_time:.1f} seconds."
            logger.warning(error_msg)
            await self.emitter.emit(status="error", description=f"❌ {error_msg}", done=True)
            raise RateLimitExceededError(error_msg)
            
        await self.emitter.emit(f"🔍 Accessing URL: {url}", step_number=1)
        cached_result = website_cache.get(url)
        
        if cached_result and CacheValidator.is_valid(cached_result, self.valves.CACHE_MAX_AGE_MINUTES):
            await self.emitter.emit("📑 Content retrieved from cache", step_number=3)
            result_data = cached_result.copy()
            soup = None
            error = result_data.get("error")
        else:
            if cached_result:
                logger.info(f"Cache entry for {url} is stale (age > {self.valves.CACHE_MAX_AGE_MINUTES} minutes). Refreshing.")
            await self.emitter.emit("🌐 Fetching web content (not cached)", step_number=2)
            try:
                result_data = await self._get_website_content_cached(url)
                cache_copy = result_data.copy()
                soup = cache_copy.pop("soup", None)
                if not result_data.get("error"):
                    website_cache[url] = cache_copy
                error = result_data.get("error")
            except Exception as e:
                error_msg = f"Failed to fetch website content: {str(e)}"
                logger.error(error_msg)
                await self.emitter.emit(status="error", description=f"❌ {error_msg}", done=True)
                raise WebScrapingError(error_msg) from e
                
        if error:
            await self.emitter.emit(status="error", description=f"❌ Error accessing page: {error}", done=True)
            return f"Error accessing {result_data.get('url', 'URL')}: {error}"
        else:
            if self.valves.CITATION_LINKS and soup:
                await self.emitter.emit("📚 Generating citations", step_number=6)
                await self.emitter.emit_citation(soup, result_data)
            await self.emitter.emit(status="complete", description="✅ Website content processed successfully.", done=True, step_number=7)
            output_parts = [
                f"**Title:** {result_data.get('title', 'N/A')}",
                f"**URL:** {result_data.get('url', 'N/A')}",
                f"**Date Accessed:** {result_data.get('date_accessed', 'N/A')}",
                "\n**Excerpt:**",
                result_data.get('excerpt', ''),
                "\n\n**Content:**", # Added extra \n for spacing
                result_data.get('content', '')
            ]
            if result_data.get("error"): # Ensure error is bolded if it exists at this stage
                output_parts.insert(2, f"**Error:** {result_data.get('error')}")
            return "\n".join(output_parts)

    async def close_client(self):
        await self.client.aclose()

    def get_current_datetime(self) -> str:
        now_utc = datetime.now(timezone.utc)
        try:
            tz = ZoneInfo(self.valves.desired_timezone)
        except Exception:
            tz = timezone.utc
        now_desired = now_utc.astimezone(tz)
        formatted_datetime = now_desired.strftime("%A, %B %d, %Y at %I:%M %p (%Z)")
        return f"The current date and time is {formatted_datetime}"

# --- FastMCP HTTP Server ---
_fastmcp = FastMCP("mcp-searxng-enhanced", version="1.1.0")
_http_tools: Optional[Tools] = None

def _get_http_tools() -> Tools:
    global _http_tools
    if _http_tools is None:
        _http_tools = Tools()
    return _http_tools

@_fastmcp.tool(
    description="Search the web for various categories (general, images, videos, files, map, social media, news, it, science). Scrapes text for web categories, returns specific data for others. Provides citations. Allows optional filtering. Is able to read PDF files and convert to Markdown."
)
async def search_web(
    query: str,
    engines: Optional[str] = None,
    category: str = "general",
    safesearch: Optional[str] = None,
    time_range: Optional[str] = None,
) -> str:
    return await _get_http_tools().search_web(query, engines, category, safesearch, time_range)

@_fastmcp.tool(
    description="Scrape content from web pages (using Trafilatura, converting Reddit to old.reddit). Caches results and provides citations. Is able to read PDF files and convert these to Markdown."
)
async def get_website(url: str) -> str:
    return await _get_http_tools().get_website(url)

@_fastmcp.tool(
    description="Get the current date and time in the configured timezone."
)
def get_current_datetime() -> str:
    return _get_http_tools().get_current_datetime()

# --- JSON-RPC Communication ---
async def send_json_rpc(data: Dict[str, Any]):
    message_str = json.dumps(data)
    sys.stdout.write(f"{message_str}\n")
    sys.stdout.flush()

async def send_notification(method: str, params: Any):
    await send_json_rpc({"jsonrpc": "2.0", "method": method, "params": params})

# --- Main Server Loop ---
async def main():
    tools_instance = Tools(send_notification_func=send_notification)
    logger.info("MCP Server Tools instance created.")
    logger.info("MCP Server entering main loop...")
    while True:
        line = sys.stdin.readline()
        if not line:
            logger.info("MCP Server: EOF received, exiting main loop.")
            break
        try:
            request = json.loads(line)
            request_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})
            response = {"jsonrpc": "2.0", "id": request_id}
            logger.info(f"MCP Server received method: {method!r} (ID: {request_id})")
            if method == "initialize":
                response["result"] = {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "mcp-searxng-enhanced", "version": "1.1.0"},
                    "capabilities": {
                        "tools": {
                            "search_web": {
                                "description": "Search the web for various categories (general, images, videos, files, map, social media, news, it, science). Scrapes text for web categories, returns specific data for others. Provides citations. Allows optional filtering. Is able to read PDF files and convert to Markdown.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {"type": "string", "description": "The search query."},
                                        "engines": {"type": "string", "description": "Optional comma-separated list of SearXNG engines (e.g., 'google,wikipedia'). Defaults to instance settings."},
                                        "category": {"type": "string", "description": "Optional SearXNG category (e.g., 'general', 'images', 'videos', 'files', 'map', 'social media', 'news', 'it', 'science'). Defaults to 'general'."},
                                        "safesearch": {"type": "string", "enum": ["0", "1", "2"], "description": "Optional safe search level (0: None, 1: Moderate, 2: Strict). Defaults to instance settings."},
                                        "time_range": {"type": "string", "enum": ["day", "month", "year"], "description": "Optional time range filter ('day', 'month', 'year'). Defaults to instance settings."}
                                    },
                                    "required": ["query"],
                                },
                            },
                            "get_website": {
                                "description": "Scrape content from web pages (using Trafilatura, converting Reddit to old.reddit). Caches results and provides citations. Is able to read PDF files and convert these to Markdown.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "url": {"type": "string", "description": "The URL of the website."},
                                    },
                                    "required": ["url"],
                                },
                            },
                            "get_current_datetime": {
                                "description": "Get the current date and time in the configured timezone.",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                        }
                    }
                }
            elif method == "tools/list":
                response["result"] = {
                    "tools": [
                        {
                            "name": "search_web",
                            "description": "Search the web for various categories (general, images, videos, files, map, social media, news, it, science). Scrapes text for web categories, returns specific data for others. Provides citations. Allows optional filtering. Is able to read PDF files and convert to Markdown.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "The search query."},
                                    "engines": {"type": "string", "description": "Optional comma-separated list of SearXNG engines (e.g., 'google,wikipedia'). Defaults to instance settings."},
                                    "category": {"type": "string", "description": "Optional SearXNG category (e.g., 'general', 'images', 'videos', 'files', 'map', 'social media', 'news', 'it', 'science'). Defaults to 'general'."},
                                    "safesearch": {"type": "string", "enum": ["0", "1", "2"], "description": "Optional safe search level (0: None, 1: Moderate, 2: Strict). Defaults to instance settings."},
                                    "time_range": {"type": "string", "enum": ["day", "month", "year"], "description": "Optional time range filter ('day', 'month', 'year'). Defaults to instance settings."}
                                },
                                "required": ["query"],
                            },
                        },
                        {
                            "name": "get_website",
                            "description": "Scrape content from web pages (using Trafilatura, converting Reddit to old.reddit). Caches results and provides citations. Is able to read PDF files and convert these to Markdown.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "url": {"type": "string", "description": "The URL of the website."},
                                },
                                "required": ["url"],
                            },
                        },
                        {
                            "name": "get_current_datetime",
                            "description": "Get the current date and time in the configured timezone.",
                            "inputSchema": {"type": "object", "properties": {}},
                        },
                    ]
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                try:                    # Tool aliases as per Cline Rule document
                    alias_map = {
                        # search_web aliases
                        "search": "search_web",
                        "web_search": "search_web",
                        "find": "search_web",
                        "lookup_web": "search_web",
                        "search_online": "search_web",
                        "access_internet": "search_web",
                        
                        # get_website aliases
                        "fetch_url": "get_website",
                        "scrape_page": "get_website",
                        "get": "get_website",
                        "load_website": "get_website",
                        
                        # get_current_datetime aliases
                        "current_time": "get_current_datetime",
                        "get_time": "get_current_datetime",
                        "current_date": "get_current_datetime"
                    }                    # Handle the context-sensitive 'lookup' alias as per Cline Rule
                    if tool_name == "lookup":
                        # If called with a 'url' argument, map to 'get_website'
                        # Otherwise, map to 'search_web'
                        if "url" in tool_args and tool_args["url"]:
                            canonical_name = "get_website"
                        else:
                            canonical_name = "search_web"
                        logger.info(f"Context-sensitive alias: Mapping 'lookup' to '{canonical_name}' based on arguments")
                        tool_name = canonical_name
                    elif tool_name in alias_map:
                        canonical_name = alias_map[tool_name]
                        logger.info(f"Aliasing tool call from '{tool_name}' to '{canonical_name}'")
                        tool_name = canonical_name
                    if tool_name == "search_web":
                        query = tool_args.get("query")
                        if not query:
                            raise ValueError("Missing 'query' argument for search_web")
                        engines = tool_args.get("engines")
                        category = tool_args.get("category", "general")
                        safesearch = tool_args.get("safesearch")
                        time_range = tool_args.get("time_range")
                        result_text = await tools_instance.search_web(query, engines, category, safesearch, time_range)
                        response["result"] = {"content": [{"type": "text", "text": result_text}], "isError": False}
                    elif tool_name == "get_website":
                        url = tool_args.get("url")
                        if not url:
                            raise ValueError("Missing 'url' argument for get_website")
                        result_text = await tools_instance.get_website(url)
                        response["result"] = {"content": [{"type": "text", "text": result_text}], "isError": False}
                    elif tool_name == "get_current_datetime":
                        datetime_str = tools_instance.get_current_datetime()
                        response["result"] = {"content": [{"type": "text", "text": datetime_str}], "isError": False}
                    else:
                        raise ValueError(f"Unknown tool: {tool_name}")
                except Exception as e:
                    response["result"] = {"content": [{"type": "text", "text": str(e)}], "isError": True}
            else:
                response["error"] = {"code": -32601, "message": "Method not found"}
            if request_id is not None:
                logger.info(f"Sending response for request ID: {request_id}")
                await send_json_rpc(response)
            else:
                logger.info(f"Received notification (no ID), method: {method}")
        except json.JSONDecodeError:
            if line.strip():
                logger.error(f"JSON Parse error processing line: {line!r}")
                error_response = {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}
                await send_json_rpc(error_response)
        except Exception as e:
            req_id = request.get("id") if isinstance(request, dict) else None
            logger.exception(f"Internal error processing request (ID: {req_id}): {line!r}")
            error_response = {"jsonrpc": "2.0", "error": {"code": -32603, "message": f"Internal error: {str(e)}"}, "id": req_id}
            await send_json_rpc(error_response)
    logger.info("Closing HTTP client.")
    await tools_instance.close_client()
    logger.info("MCP Server exiting.")

if __name__ == "__main__":
    if "--http" in sys.argv:
        http_host = os.getenv("MCP_HTTP_HOST", "0.0.0.0")
        http_port = int(os.getenv("MCP_HTTP_PORT", "8000"))
        _get_http_tools()  # eagerly init so config file is written on start
        logger.info(f"Starting FastMCP HTTP server on {http_host}:{http_port}/mcp")
        _fastmcp.run(
            transport="http",
            host=http_host,
            port=http_port,
            path="/mcp",
            stateless_http=True,
            middleware=[
                Middleware(
                    CORSMiddleware,
                    allow_origins=["*"],
                    allow_methods=["*"],
                    allow_headers=["*"],
                )
            ],
        )
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received, exiting.")
            sys.exit(0)
        except Exception as e:
            logging.critical(f"Fatal error starting server: {e}", exc_info=True)
            sys.exit(1)
