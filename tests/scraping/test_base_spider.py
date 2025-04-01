import pytest
from unittest.mock import Mock, patch

from src.scraping.config import ScraperConfig
from src.scraping.spiders.base_spider import BaseContentSpider

class TestBaseSpider(BaseContentSpider):
    def extract_story(self, content):
        return content

def test_spider_config_validation():
    """Test spider configuration validation."""
    valid_config = ScraperConfig(allowed_domains=['example.com'])
    spider = TestBaseSpider(valid_config)
    assert spider.config == valid_config

def test_spider_invalid_config():
    """Test validation of invalid scraper configurations."""
    with pytest.raises(ValueError):
        ScraperConfig(allowed_domains=[])

def test_is_allowed_domain():
    """Test domain allowance mechanism."""
    config = ScraperConfig(allowed_domains=['medium.com'])
    spider = TestBaseSpider(config)
    
    assert spider._is_allowed_domain('https://medium.com/story') == True
    assert spider._is_allowed_domain('https://example.com/story') == False

@patch('requests.get')
def test_fetch_content_success(mock_get):
    """Test successful content fetching."""
    mock_response = Mock()
    mock_response.text = 'Sample content'
    mock_response.status_code = 200
    mock_response.headers = {'Content-Type': 'text/html'}
    mock_get.return_value = mock_response

    config = ScraperConfig(allowed_domains=['example.com'])
    spider = TestBaseSpider(config)
    
    result = spider.fetch_content('https://example.com/story')
    
    assert result['content'] == 'Sample content'
    assert result['status_code'] == 200

@patch('requests.get')
def test_fetch_content_forbidden_domain(mock_get):
    """Test handling of forbidden domains."""
    config = ScraperConfig(allowed_domains=['medium.com'])
    spider = TestBaseSpider(config)
    
    result = spider.fetch_content('https://example.com/story')
    
    assert result == {}
    mock_get.assert_not_called()
