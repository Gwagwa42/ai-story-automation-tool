from typing import Dict, Any
from bs4 import BeautifulSoup

from .base_spider import BaseContentSpider
from ..config import ScraperConfig

class MediumSpider(BaseContentSpider):
    """
    Specialized spider for scraping story content from Medium.
    
    Focuses on extracting meaningful narrative content while
    respecting platform guidelines and content complexity.
    """
    
    def __init__(
        self, 
        config: ScraperConfig = None
    ):
        """
        Initialize Medium spider with optional configuration.
        
        Args:
            config (ScraperConfig, optional): Custom scraping configuration
        """
        if config is None:
            config = ScraperConfig(allowed_domains=['medium.com'])
        
        super().__init__(config)
    
    def extract_story(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured story content from Medium article.
        
        Args:
            content (Dict[str, Any]): Raw fetched content
        
        Returns:
            Dict[str, Any]: Structured story metadata
        """
        if not content or 'content' not in content:
            return {}
        
        try:
            soup = BeautifulSoup(content['content'], 'html.parser')
            
            # Extract article title
            title = soup.find('h1', {'class': 'pw-title'})
            title = title.text.strip() if title else 'Untitled'
            
            # Extract article body
            article_body = soup.find('div', {'class': 'pw-post-body'})
            paragraphs = article_body.find_all('p') if article_body else []
            
            # Extract story text
            story_text = ' '.join(
                paragraph.text.strip() 
                for paragraph in paragraphs
            )
            
            # Basic metadata extraction
            author = soup.find('meta', {'name': 'author'})
            published_time = soup.find('meta', {'property': 'article:published_time'})
            
            return {
                'url': content.get('url', ''),
                'title': title,
                'text': story_text,
                'author': author['content'] if author else 'Unknown',
                'published_at': published_time['content'] if published_time else None,
                'platform': 'Medium'
            }
        
        except Exception as e:
            self.logger.error(f"Error extracting Medium story: {e}")
            return {}
