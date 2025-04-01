from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ScraperConfig:
    """
    Configuration for web scraping operations.
    Provides flexible, ethical scraping parameters.
    """
    # Allowed domains for scraping
    allowed_domains: List[str] = None

    # Delay between requests to prevent server overload
    request_delay: float = 1.0

    # Maximum number of concurrent requests
    max_concurrent_requests: int = 5

    # Timeout for individual request
    request_timeout: float = 10.0

    # User agent for ethical web crawling
    user_agent: str = (
        "AIStoryAutomationTool/0.1.0 "
        "(https://github.com/Gwagwa42/ai-story-automation-tool; "
        "research@aistorytool.com)"
    )

    # Respect robots.txt by default
    respect_robots_txt: bool = True

    # Additional headers for request customization
    extra_headers: Optional[Dict[str, str]] = None

    # Logging configuration
    log_level: str = 'INFO'

    def validate(self):
        """
        Validate scraper configuration.
        Ensures ethical and responsible scraping parameters.
        """
        if not self.allowed_domains:
            raise ValueError("At least one allowed domain must be specified")
        
        if self.request_delay < 0:
            raise ValueError("Request delay must be non-negative")
        
        if self.max_concurrent_requests < 1:
            raise ValueError("At least one concurrent request is required")

# Default configuration for general web scraping
DEFAULT_SCRAPER_CONFIG = ScraperConfig(
    allowed_domains=['medium.com', 'substack.com', 'news.ycombinator.com']
)
