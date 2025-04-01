from datetime import datetime, timedelta
import pytest
from src.scraping.content_relevance import RelevanceScorer

def create_test_story(
    text: str = "", 
    published_at: str = None, 
    platform: str = "test"
) -> dict:
    """
    Helper function to create a standardized test story dictionary.
    
    Args:
        text (str): Story text content
        published_at (str): Publication timestamp
        platform (str): Story source platform
    
    Returns:
        dict: Structured story metadata
    """
    if published_at is None:
        published_at = datetime.now().isoformat()
    
    return {
        "text": text,
        "published_at": published_at,
        "platform": platform
    }

class TestContentRelevanceScorer:
    """
    Comprehensive test suite for the content relevance scoring system.
    
    Validates scoring across multiple dimensions:
    - Timeliness
    - Content depth
    - Language complexity
    - Engagement potential
    """
    
    def test_minimum_word_count_validation(self):
        """
        Verify that stories below the minimum word count are rejected.
        
        Ensures the relevance scorer maintains a quality threshold
        by filtering out extremely short content.
        """
        scorer = RelevanceScorer(min_word_count=250)
        
        # Short story should receive zero relevance
        short_story = create_test_story(text="Few words here.")
        assert scorer.score_story(short_story) == 0.0
        
        # Story meeting minimum word count
        long_story = create_test_story(
            text=" ".join(["word"] * 300)
        )
        assert scorer.score_story(long_story) > 0.0
    
    def test_timeliness_scoring(self):
        """
        Test the timeliness dimension of content scoring.
        
        Validates that:
        - Recent stories receive higher scores
        - Old stories receive progressively lower scores
        - Stories beyond max age receive zero relevance
        """
        scorer = RelevanceScorer(max_age_days=30)
        
        # Story published just now
        recent_story = create_test_story(
            text=" ".join(["word"] * 300),
            published_at=datetime.now().isoformat()
        )
        assert scorer.score_story(recent_story) > 0.9
        
        # Story published 15 days ago
        mid_age_story = create_test_story(
            text=" ".join(["word"] * 300),
            published_at=(datetime.now() - timedelta(days=15)).isoformat()
        )
        mid_score = scorer.score_story(mid_age_story)
        assert 0.5 <= mid_score <= 0.7
        
        # Story published 45 days ago
        old_story = create_test_story(
            text=" ".join(["word"] * 300),
            published_at=(datetime.now() - timedelta(days=45)).isoformat()
        )
        assert scorer.score_story(old_story) == 0.0
    
    def test_depth_scoring(self):
        """
        Evaluate the content depth scoring mechanism.
        
        Ensures that:
        - Longer stories receive higher depth scores
        - Score scales logarithmically
        - Maximum depth is capped at 1.0
        """
        scorer = RelevanceScorer()
        
        # Short story
        short_story = create_test_story(
            text=" ".join(["word"] * 500)
        )
        short_score = scorer.score_story(short_story)
        assert 0.2 <= short_score <= 0.4
        
        # Medium-length story
        medium_story = create_test_story(
            text=" ".join(["word"] * 1000)
        )
        medium_score = scorer.score_story(medium_story)
        assert 0.4 <= medium_score <= 0.6
        
        # Very long story
        long_story = create_test_story(
            text=" ".join(["word"] * 2500)
        )
        long_score = scorer.score_story(long_story)
        assert long_score >= 0.9
    
    def test_complexity_scoring(self):
        """
        Test the linguistic complexity scoring mechanism.
        
        Validates that:
        - Complex language receives higher scores
        - Simple language receives lower scores
        - Scoring considers average word length
        """
        scorer = RelevanceScorer()
        
        # Simple language story
        simple_story = create_test_story(
            text="The cat sat on the mat."
        )
        simple_score = scorer.score_story(simple_story)
        assert simple_score < 0.3
        
        # Complex language story
        complex_story = create_test_story(
            text="The sophisticated algorithmic infrastructure demonstrates remarkable computational efficiency."
        )
        complex_score = scorer.score_story(complex_story)
        assert complex_score > 0.6
    
    def test_engagement_scoring(self):
        """
        Evaluate the engagement potential scoring.
        
        Ensures that:
        - Stories with engagement keywords boost relevance
        - Keyword matches are proportionally scored
        - Maximum engagement score is 1.0
        """
        scorer = RelevanceScorer()
        
        # Story with multiple engagement keywords
        high_engagement_story = create_test_story(
            text="A breakthrough innovation that will transform technological research."
        )
        high_score = scorer.score_story(high_engagement_story)
        assert high_score > 0.7
        
        # Story with no engagement keywords
        low_engagement_story = create_test_story(
            text="A simple story about everyday events."
        )
        low_score = scorer.score_story(low_engagement_story)
        assert low_score < 0.3
    
    def test_comprehensive_scoring(self):
        """
        Perform an integrated test of the entire scoring system.
        
        Validates that multiple scoring dimensions interact correctly
        and produce a balanced, meaningful relevance score.
        """
        scorer = RelevanceScorer()
        
        comprehensive_story = create_test_story(
            text=" ".join(["complex", "innovative", "breakthrough"] * 100),
            published_at=(datetime.now() - timedelta(days=7)).isoformat()
        )
        
        score = scorer.score_story(comprehensive_story)
        
        # A comprehensive, high-quality story should score highly
        assert 0.7 <= score <= 1.0
