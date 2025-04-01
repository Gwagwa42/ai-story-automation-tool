from typing import Dict, List, Any
from datetime import datetime, timedelta
import re
import math

class RelevanceScorer:
    """
    Intelligent content relevance scoring system.
    
    Evaluates story content across multiple dimensions.
    """
    
    def __init__(
        self, 
        timeliness_weight: float = 0.3,
        depth_weight: float = 0.3,
        complexity_weight: float = 0.2,
        engagement_weight: float = 0.2,
        min_word_count: int = 250,
        max_age_days: int = 30
    ):
        """
        Initialize the relevance scorer with configurable weights.
        
        Args:
            timeliness_weight (float): Weight for publication recency
            depth_weight (float): Weight for content depth
            complexity_weight (float): Weight for linguistic complexity
            engagement_weight (float): Weight for engagement potential
            min_word_count (int): Minimum words for valid content
            max_age_days (int): Maximum days for content relevance
        """
        self.timeliness_weight = timeliness_weight
        self.depth_weight = depth_weight
        self.complexity_weight = complexity_weight
        self.engagement_weight = engagement_weight
        self.min_word_count = min_word_count
        self.max_age_days = max_age_days
        
        self.engagement_keywords = [
            'breakthrough', 'innovation', 'research', 
            'discover', 'transform', 'revolutionary',
            'impact', 'future', 'technology'
        ]
    
    def score_story(self, story: Dict[str, Any]) -> float:
        """
        Calculate a comprehensive relevance score for a story.
        
        Args:
            story (Dict[str, Any]): Story metadata
        
        Returns:
            float: Overall relevance score (0-1)
        """
        # Validate basic story requirements
        text = story.get('text', '')
        word_count = len(text.split())
        
        if word_count < self.min_word_count:
            return 0.0
        
        # Calculate individual dimension scores
        timeliness = self._calculate_timeliness(story)
        depth = self._calculate_depth(text)
        complexity = self._calculate_complexity(text)
        engagement = self._calculate_engagement(text)
        
        # Weighted score calculation
        total_score = (
            timeliness * self.timeliness_weight +
            depth * self.depth_weight +
            complexity * self.complexity_weight +
            engagement * self.engagement_weight
        )
        
        return max(0, min(total_score, 1))
    
    def _calculate_timeliness(self, story: Dict[str, Any]) -> float:
        """
        Calculate story timeliness based on publication date.
        
        Args:
            story (Dict[str, Any]): Story metadata
        
        Returns:
            float: Timeliness score (0-1)
        """
        published_at = story.get('published_at')
        if not published_at:
            return 0.5
        
        try:
            publication_date = datetime.fromisoformat(published_at)
            age_days = (datetime.now() - publication_date).days
            
            if age_days > self.max_age_days:
                return 0.0
            
            # Exponential decay with more aggressive recent content boost
            return 1 - (age_days / self.max_age_days) ** 2
        
        except (TypeError, ValueError):
            return 0.5
    
    def _calculate_depth(self, text: str) -> float:
        """
        Calculate content depth based on word count.
        
        Args:
            text (str): Story text
        
        Returns:
            float: Depth score (0-1)
        """
        word_count = len(text.split())
        
        # Logarithmic scaling with adjusted parameters
        depth_score = math.log(max(word_count, 1), 1000)
        return max(0, min(depth_score, 1))
    
    def _calculate_complexity(self, text: str) -> float:
        """
        Estimate linguistic complexity.
        
        Args:
            text (str): Story text
        
        Returns:
            float: Complexity score (0-1)
        """
        words = text.split()
        if not words:
            return 0.0
        
        # Calculate average word length and unique word ratio
        avg_word_length = sum(len(word) for word in words) / len(words)
        unique_words = len(set(words)) / len(words)
        
        # Combined complexity metric
        complexity_score = (avg_word_length / 8) * unique_words
        return max(0, min(complexity_score, 1))
    
    def _calculate_engagement(self, text: str) -> float:
        """
        Calculate engagement potential.
        
        Args:
            text (str): Story text
        
        Returns:
            float: Engagement score (0-1)
        """
        text_lower = text.lower()
        
        # Count keyword matches with more sophisticated scoring
        keyword_matches = sum(
            1 for keyword in self.engagement_keywords 
            if keyword in text_lower
        )
        
        # Weighted keyword scoring
        max_keywords = len(self.engagement_keywords)
        engagement_score = min(keyword_matches / max_keywords, 1)
        
        return engagement_score
