from typing import Dict, Any
from bs4 import BeautifulSoup
from datetime import datetime
import re

from .base_spider import BaseContentSpider
from ..config import ScraperConfig

class SubstackSpider(BaseContentSpider):
    """
    Specialized spider for extracting story content from Substack publications.
    
    This spider is designed to handle the unique content structure of Substack,
    which often features long-form written content with distinct formatting.
    
    Key Considerations:
    - Handles both free and paid content sections
    - Extracts metadata like publication date and author
    - Preserves content formatting nuances
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
        
        # Remove HTML entities
        text = re.sub(r'&[a-zA-Z]+;', ' ', text)
        
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
            
            # Extract title
            title = soup.find('h1', class_='post-title')
            title = title.text.strip() if title else 'Untitled'
            
            # Extract full article body
            article_body = soup.find('div', class_=['body', 'markup'])
            
            if not article_body:
                # Fallback to more generic selection
                article_body = soup.find('article')
            
            # Extract paragraphs
            paragraphs = article_body.find_all(['p', 'div'], class_=['paragraph', 'block'])
            
            # Combine paragraphs into story text
            story_text = ' '.join(
                self._clean_text(paragraph.get_text(strip=True)) 
                for paragraph in paragraphs 
                if paragraph.get_text(strip=True)
            )
            
            # Extract publication metadata
            author = soup.find('meta', {'name': 'author'})
            published_time = soup.find('time')
            
            # Parse publication date
            publication_date = None
            if published_time and published_time.get('datetime'):
                try:
                    publication_date = datetime.fromisoformat(
                        published_time['datetime']
                    ).isoformat()
                except ValueError:
                    self.logger.warning(f"Could not parse date: {published_time['datetime']}")
            
            return {
                'url': content.get('url', ''),
                'title': title,
                'text': story_text,
                'author': author['content'] if author else 'Unknown Author',
                'published_at': publication_date,
                'platform': 'Substack',
                'word_count': len(story_text.split()),
                'reading_time_minutes': max(1, len(story_text.split()) // 250)
            }
        
        except Exception as e:
            self.logger.error(f"Error extracting Substack story: {e}")
            return {}
