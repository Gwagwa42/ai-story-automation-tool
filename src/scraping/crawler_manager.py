import asyncio
import logging
from typing import List, Dict, Any, Type

from .config import ScraperConfig, DEFAULT_SCRAPER_CONFIG
from .content_relevance import RelevanceScorer
from .spiders.base_spider import BaseContentSpider
from .spiders.medium_spider import MediumSpider
from .spiders.substack_spider import SubstackSpider

class CrawlerManager:
    """
    Centralized management system for coordinating web content discovery.
    
    Responsibilities:
    - Manage multiple content spiders
    - Coordinate parallel story extraction
    - Apply content relevance filtering
    - Provide a unified interface for story discovery
    """
    
    def __init__(
        self, 
        config: ScraperConfig = DEFAULT_SCRAPER_CONFIG,
        relevance_scorer: RelevanceScorer = None,
        logger: logging.Logger = None
    ):
        """
        Initialize the crawler manager with optional configuration.
        
        Args:
            config (ScraperConfig): Global scraping configuration
            relevance_scorer (RelevanceScorer): Custom relevance scoring system
            logger (logging.Logger): Custom logger instance
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.relevance_scorer = relevance_scorer or RelevanceScorer()
        
        # Define available content spiders
        self.spiders: List[Type[BaseContentSpider]] = [
            MediumSpider,
            SubstackSpider
        ]
    
    async def discover_stories(
        self, 
        urls: List[str], 
        max_stories: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Discover and extract stories from multiple URLs.
        
        Args:
            urls (List[str]): List of URLs to explore
            max_stories (int): Maximum number of stories to return
        
        Returns:
            List[Dict[str, Any]]: Extracted and scored stories
        """
        tasks = []
        for url in urls:
            for spider_cls in self.spiders:
                spider = spider_cls(self.config)
                task = asyncio.create_task(self._extract_story(spider, url))
                tasks.append(task)
        
        # Wait for all tasks to complete
        story_results = await asyncio.gather(*tasks)
        
        # Filter and score stories
        scored_stories = [
            story for story in story_results 
            if story and self.relevance_scorer.score_story(story) > 0.5
        ]
        
        # Sort by relevance and truncate
        scored_stories.sort(
            key=lambda s: self.relevance_scorer.score_story(s), 
            reverse=True
        )
        
        return scored_stories[:max_stories]
    
    async def _extract_story(
        self, 
        spider: BaseContentSpider, 
        url: str
    ) -> Dict[str, Any]:
        """
        Extract a single story using a specific spider.
        
        Args:
            spider (BaseContentSpider): Spider to use for extraction
            url (str): URL to extract story from
        
        Returns:
            Dict[str, Any]: Extracted story or empty dict
        """
        try:
            # Fetch raw content
            content = spider.fetch_content(url)
            
            # Extract structured story
            if content:
                story = spider.extract_story(content)
                return story
        
        except Exception as e:
            self.logger.error(f"Story extraction error: {e}")
        
        return {}
    
    def add_spider(self, spider_cls: Type[BaseContentSpider]):
        """
        Dynamically add a new spider to the discovery system.
        
        Args:
            spider_cls (Type[BaseContentSpider]): Spider class to add
        """
        if spider_cls not in self.spiders:
            self.spiders.append(spider_cls)
            self.logger.info(f"Added spider: {spider_cls.__name__}")
