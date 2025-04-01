import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from urllib.parse import urlparse

import requests
from requests.exceptions import RequestException

from ..config import ScraperConfig, DEFAULT_SCRAPER_CONFIG

class BaseContentSpider(ABC):
    """
    Abstract base class for intelligent, ethical web content extraction.
    
    Provides a standardized framework for web scraping with built-in
    ethical considerations and extensibility.
    """
    
    def __init__(
        self, 
        config: ScraperConfig = DEFAULT_SCRAPER_CONFIG,
        logger: logging.Logger = None
    ):
        """
        Initialize the spider with configuration and logging.
        
        Args:
            config (ScraperConfig): Scraping configuration
            logger (logging.Logger, optional): Custom logger
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self._validate_config()
    
    def _validate_config(self):
        """
        Validate spider configuration before scraping.
        Ensures ethical and safe scraping parameters.
        """
        try:
            self.config.validate()
        except ValueError as e:
            self.logger.error(f"Invalid scraper configuration: {e}")
            raise
    
    def _get_request_headers(self) -> Dict[str, str]:
        """
        Generate request headers with ethical considerations.
        
        Returns:
            Dict[str, str]: Request headers
        """
        headers = {
            'User-Agent': self.config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/'
        }
        
        if self.config.extra_headers:
            headers.update(self.config.extra_headers)
        
        return headers
    
    def _is_allowed_domain(self, url: str) -> bool:
        """
        Check if the URL is within allowed domains.
        
        Args:
            url (str): URL to validate
        
        Returns:
            bool: Whether the URL is allowed
        """
        parsed_url = urlparse(url)
        return any(
            domain in parsed_url.netloc 
            for domain in self.config.allowed_domains
        )
    
    def fetch_content(self, url: str) -> Dict[str, Any]:
        """
        Fetch content from a given URL with robust error handling.
        
        Args:
            url (str): URL to scrape
        
        Returns:
            Dict[str, Any]: Scraped content metadata
        """
        if not self._is_allowed_domain(url):
            self.logger.warning(f"URL {url} not in allowed domains")
            return {}
        
        try:
            response = requests.get(
                url, 
                headers=self._get_request_headers(),
                timeout=self.config.request_timeout
            )
            
            response.raise_for_status()
            
            return {
                'url': url,
                'content': response.text,
                'status_code': response.status_code,
                'headers': dict(response.headers)
            }
        
        except RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return {}
    
    @abstractmethod
    def extract_story(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Abstract method to extract story content.
        Must be implemented by specific content spiders.
        
        Args:
            content (Dict[str, Any]): Raw fetched content
        
        Returns:
            Dict[str, Any]: Extracted story metadata
        """
        pass
