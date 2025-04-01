from typing import Dict, Any
from bs4 import BeautifulSoup
from datetime import datetime
import re
import math

from .base_spider import BaseContentSpider
from ..config import ScraperConfig

class SubstackSpider(BaseContentSpider):
    """
    Specialized spider for extracting story content from Substack publications.
    
    This spider is designed to handle the unique content structure of Substack,
    which often features long-form written content with distinct formatting.
    """
    
    def __init__(
        self, 
        config: ScraperConfig = None
    ):
        """
        Initialize Substack spider with optional configuration.
        
        Args:
            config (ScraperConfig, optional): Custom scraping configuration
        """
        if config is None:
            config = ScraperConfig(allowed_domains=['substack.com'])
        
        super().__init__(config)
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text (str): Raw extracted text
        
        Returns:
            str: Cleaned and normalized text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove HTML entities systematically
        text = re.sub(r'&[a-zA-Z]+;', '', text).strip()
        
        return text
    
    def extract_story(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured story content from Substack article.
        
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
            title = soup.find('h1', {'class': 'post-title'})
            title = title.text.strip() if title else 'Untitled'
            
            # Extract article body with multiple selector strategies
            article_body = (
                soup.find('div', {'class': ['body', 'markup', 'post-body']}) or
                soup.find('article') or
                soup.find('body')
            )
            
            # Extract paragraphs with multiple strategies
            paragraphs = article_body.find_all(['p', 'div'], class_=['paragraph', 'block', 'content'])
            
            # Combine paragraphs into story text
            story_text = ' '.join(
                self._clean_text(paragraph.get_text(strip=True)) 
                for paragraph in paragraphs 
                if paragraph.get_text(strip=True)
            )
            
            # Extract publication metadata
            author = soup.find('meta', {'name': 'author'})
            published_time = soup.find('time')
            
            # Calculate reading time
            word_count = len(story_text.split())
            reading_time = max(1, math.ceil(word_count / 250))
            
            return {
                'url': content.get('url', ''),
                'title': title,
                'text': story_text,
                'author': author['content'] if author else 'Unknown Author',
                'published_at': (
                    published_time['datetime'] if published_time and published_time.get('datetime')
                    else datetime.now().isoformat()
                ),
                'platform': 'Substack',
                'word_count': word_count,
                'reading_time_minutes': reading_time
            }
        
        except Exception as e:
            self.logger.error(f"Error extracting Substack story: {e}")
            return {}
