from typing import Dict, List, Any
from datetime import datetime, timedelta
import re
from dataclasses import dataclass, field
import math

@dataclass
class RelevanceScorer:
    """
    Intelligent content relevance scoring system.
    
    Evaluates story content across multiple dimensions.
    """
    
    # Scoring dimension weights
    timeliness_weight: float = 0.3
    depth_weight: float = 0.3
    complexity_weight: float = 0.2
    engagement_weight: float = 0.2
    
    # Thresholds and configuration
    min_word_count: int = 250
    max_age_days: int = 30
    
    # Engagement keywords that boost relevance
    engagement_keywords: List[str] = field(default_factory=lambda: [
        'breakthrough', 'innovation', 'research', 
        'discover', 'transform', 'revolutionary',
        'impact', 'future', 'technology'
    ])
    
    def score_story(self, story: Dict[str, Any]) -> float:
        """
        Calculate a comprehensive relevance score for a story.
        
        Args:
            story (Dict[str, Any]): Story metadata
        
        Returns:
            float: Overall relevance score (0-1)
        """
        # Validate basic story requirements
        word_count = len(story.get('text', '').split())
        if word_count < self.min_word_count:
            return 0.0
        
        # Calculate individual dimension scores
        timeliness_score = self._calculate_timeliness(story)
        depth_score = self._calculate_depth(story)
        complexity_score = self._calculate_complexity(story)
        engagement_score = self._calculate_engagement(story)
        
        # Weighted combination of scores
        total_score = (
            timeliness_score * self.timeliness_weight +
            depth_score * self.depth_weight +
            complexity_score * self.complexity_weight +
            engagement_score * self.engagement_weight
        )
        
        # Normalize and bound the score
        return max(0, min(total_score, 1))
    
    def _calculate_timeliness(self, story: Dict[str, Any]) -> float:
        """
        Calculate story timeliness score based on publication date.
        
        Args:
            story (Dict[str, Any]): Story metadata
        
        Returns:
            float: Timeliness score (0-1)
        """
        published_at = story.get('published_at')
        if not published_at:
            return 0.5  # Neutral score if no date
        
        try:
            publication_date = datetime.fromisoformat(published_at)
            age_days = (datetime.now() - publication_date).days
            
            # Exponential decay of relevance
            if age_days > self.max_age_days:
                return 0.0
            
            # Use sigmoid-like curve for more nuanced scoring
            return 1 / (1 + math.exp(0.5 * (age_days - self.max_age_days/2)))
        
        except (TypeError, ValueError):
            return 0.5
    
    def _calculate_depth(self, story: Dict[str, Any]) -> float:
        """
        Assess story depth based on word count.
        
        Args:
            story (Dict[str, Any]): Story metadata
        
        Returns:
            float: Depth score (0-1)
        """
        word_count = len(story.get('text', '').split())
        
        # Logarithmic scaling with soft cap
        depth_score = math.log(max(word_count, 1), 2000)
        return max(0, min(depth_score, 1))
    
    def _calculate_complexity(self, story: Dict[str, Any]) -> float:
        """
        Estimate story complexity through linguistic analysis.
        
        Args:
            story (Dict[str, Any]): Story metadata
        
        Returns:
            float: Complexity score (0-1)
        """
        text = story.get('text', '')
        words = text.split()
        
        if not words:
            return 0.0
        
        # Calculate average word length
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # More sophisticated complexity calculation
        complexity_score = math.tanh(avg_word_length / 7)
        return max(0, min(complexity_score, 1))
    
    def _calculate_engagement(self, story: Dict[str, Any]) -> float:
        """
        Estimate potential engagement through keyword analysis.
        
        Args:
            story (Dict[str, Any]): Story metadata
        
        Returns:
            float: Engagement score (0-1)
        """
        text = story.get('text', '').lower()
        
        # Count engagement keyword matches
        keyword_matches = sum(
            1 for keyword in self.engagement_keywords 
            if keyword in text
        )
        
        # Normalize engagement score
        max_keywords = len(self.engagement_keywords)
        return min(keyword_matches / max_keywords, 1)
