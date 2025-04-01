import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from src.scraping.crawler_manager import CrawlerManager
from src.scraping.spiders.base_spider import BaseContentSpider

class MockSpider(BaseContentSpider):
    """
    Mock spider for testing crawler manager functionality.
    
    Simulates story extraction with controllable behavior.
    """
    
    def __init__(self, return_story=None, raise_exception=False):
        """
        Initialize mock spider with specific testing behavior.
        
        Args:
            return_story (dict): Story to return during extraction
            raise_exception (bool): Whether to simulate extraction failure
        """
        super().__init__()
        self.return_story = return_story or {}
        self.raise_exception = raise_exception
    
    def fetch_content(self, url):
        """Simulate content fetching."""
        return {'url': url, 'content': 'mock content'}
    
    def extract_story(self, content):
        """
        Simulate story extraction with configurable behavior.
        
        Args:
            content (dict): Fetched content
        
        Returns:
            dict: Extracted story or raises exception
        """
        if self.raise_exception:
            raise ValueError("Simulated extraction error")
        
        story = self.return_story.copy()
        story['url'] = content.get('url', '')
        return story

@pytest.mark.asyncio
class TestCrawlerManager:
    """
    Comprehensive test suite for the CrawlerManager.
    
    Validates core functionality:
    - Story discovery across multiple spiders
    - Relevance scoring integration
    - Error handling
    - Concurrent extraction
    """
    
    async def test_story_discovery_success(self):
        """
        Test successful story discovery across multiple URLs.
        
        Verifies that:
        - Multiple stories can be extracted concurrently
        - Stories are filtered by relevance
        - Maximum story limit is respected
        """
        # Prepare mock stories with varying relevance
        high_relevance_story = {
            'text': "An innovative breakthrough in technological research",
            'published_at': "2025-01-15T00:00:00Z"
        }
        low_relevance_story = {
            'text': "A simple story with few details",
            'published_at': "2024-01-01T00:00:00Z"
        }
        
        # Create crawler manager with mock spiders
        crawler = CrawlerManager()
        crawler.spiders = [
            lambda config: MockSpider(return_story=high_relevance_story),
            lambda config: MockSpider(return_story=low_relevance_story)
        ]
        
        # Simulate URLs
        test_urls = [
            'https://example1.com/story',
            'https://example2.com/story'
        ]
        
        # Discover stories
        stories = await crawler.discover_stories(test_urls, max_stories=1)
        
        # Verify results
        assert len(stories) == 1
        assert "breakthrough" in stories[0]['text']
    
    async def test_story_discovery_error_handling(self):
        """
        Test crawler's resilience to individual spider failures.
        
        Ensures that:
        - Failure in one spider doesn't halt entire discovery
        - Remaining spiders continue extraction
        """
        # Create spiders with mixed success
        crawler = CrawlerManager()
        crawler.spiders = [
            lambda config: MockSpider(raise_exception=True),
            lambda config: MockSpider(return_story={
                'text': "A successful story extraction",
                'published_at': "2025-01-15T00:00:00Z"
            })
        ]
        
        test_urls = [
            'https://example1.com/story',
            'https://example2.com/story'
        ]
        
        # Discover stories
        stories = await crawler.discover_stories(test_urls)
        
        # Verify at least one story was extracted
        assert len(stories) > 0
    
    def test_spider_registration(self):
        """
        Test dynamic spider registration.
        
        Verifies that:
        - New spiders can be added to the crawler
        - Duplicate spiders are not added
        """
        class NewMockSpider(BaseContentSpider):
            def extract_story(self, content):
                return {}
        
        crawler = CrawlerManager()
        initial_spider_count = len(crawler.spiders)
        
        # Add new spider
        crawler.add_spider(NewMockSpider)
        
        # Verify spider was added
        assert len(crawler.spiders) == initial_spider_count + 1
        
        # Try adding duplicate spider
        crawler.add_spider(NewMockSpider)
        
        # Verify no duplicate was added
        assert len(crawler.spiders) == initial_spider_count + 1
    
    async def test_empty_url_list(self):
        """
        Test crawler behavior with empty URL list.
        
        Ensures that:
        - No errors are raised
        - Empty list is returned
        """
        crawler = CrawlerManager()
        stories = await crawler.discover_stories([])
        
        assert len(stories) == 0
    
    async def test_max_stories_limit(self):
        """
        Verify that max_stories parameter works correctly.
        
        Ensures that:
        - Number of returned stories does not exceed max_stories
        - Stories are sorted by relevance
        """
        # Create multiple stories with different relevance
        stories = [
            {
                'text': f"Story {i} with varying relevance",
                'published_at': f"2025-01-{15-i:02d}T00:00:00Z"
            } for i in range(5)
        ]
        
        crawler = CrawlerManager()
        crawler.spiders = [
            lambda config: MockSpider(return_story=story) 
            for story in stories
        ]
        
        test_urls = [f'https://example{i}.com/story' for i in range(5)]
        
        # Discover limited number of stories
        discovered_stories = await crawler.discover_stories(test_urls, max_stories=3)
        
        # Verify limit and order
        assert len(discovered_stories) == 3
        
        # Check stories are sorted by relevance (most recently published first)
        timestamps = [story['published_at'] for story in discovered_stories]
        assert timestamps == sorted(timestamps, reverse=True)
