from typing import Dict, List, Any
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class RelevanceScorer:
    """
    Intelligent content relevance scoring system.
    
    Evaluates story content across multiple dimensinos to determine
    its potential value and interest level.
    
    Key Scoring Dimensions:
    - Timeliness
    - Content depth
    - Language complexity
    - Engagement potential
    """
    
    # Configurable scoring weights
    timeliness_weight: float = 0.25
    depth_weight: float = 0.3
    complexity_weight: float = 0.2
    engagement_weight: float = 0.25
    
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
            story (Dict[str, Any]): Extracted story metadata
        
        Returns:
            float: Overall relevance score (0-1)
        """
        # Validate story content
        if not self._validate_story(story):
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
        
        return min(max(total_score, 0), 1)
    
    def _validate_story(self, story: Dict[str, Any]) -> bool:
        """
        Basic validation of story content.
        
        Args:
            story (Dict[str, Any]): Story metadata
        
        Returns:
            bool: Whether story meets minimum requirements
        """
        word_count = len(story.get('text', '').split())
        return word_count >= self.min_word_count
    
    def _calculate_timeliness(self, story: Dict[str, Any]) -> float:
        """
        Calculate story timeliness score.
        
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
            age = (datetime.now() - publication_date).days
            
            # Exponential decay of relevance
            if age > self.max_age_days:
                return 0.0
            
            return 1 - (age / self.max_age_days)
        
        except (TypeError, ValueError):
            return 0.5
    
    def _calculate_depth(self, story: Dict[str, Any]) -> float:
        """
        Assess story depth based on word count and structure.
        
        Args:
            story (Dict[str, Any]): Story metadata
        
        Returns:
            float: Depth score (0-1)
        """
        word_count = len(story.get('text', '').split())
        
        # Logarithmic scaling of depth
        depth_score = min(1, (word_count / 2000))
        return depth_score
    
    def _calculate_complexity(self, story: Dict[str, Any]) -> float:
        """
        Estimate story complexity through linguistic analysis.
        
        Args:
            story (Dict[str, Any]): Story metadata
        
        Returns:
            float: Complexity score (0-1)
        """
        text = story.get('text', '')
        
        # Calculate average word length
        words = text.split()
        if not words:
            return 0.0
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Score based on word complexity
        complexity_score = min(1, avg_word_length / 7)
        return complexity_score
    
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
        
        # Normalized engagement score
        return min(keyword_matches / len(self.engagement_keywords), 1)
