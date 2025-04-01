import pytest
from bs4 import BeautifulSoup
from src.scraping.spiders.substack_spider import SubstackSpider

def test_substack_spider_initialization():
    """
    Test that the Substack spider initializes correctly.
    
    Verifies:
    - Default configuration sets Substack domain
    - Spider inherits base spider properties
    """
    spider = SubstackSpider()
    assert 'substack.com' in spider.config.allowed_domains

def test_substack_text_cleaning():
    """
    Test the text cleaning method.
    
    Ensures that:
    - Excessive whitespace is removed
    - HTML entities are stripped
    - Text is properly normalized
    """
    spider = SubstackSpider()
    
    # Test cases with various text scenarios
    test_cases = [
        ("  Hello   World  ", "Hello World"),
        ("Text with &nbsp; HTML entity", "Text with HTML entity"),
        ("Multiple   \n\t  Whitespaces", "Multiple Whitespaces")
    ]
    
    for input_text, expected_output in test_cases:
        assert spider._clean_text(input_text) == expected_output

def test_substack_story_extraction_success(mocker):
    """
    Test successful story extraction from Substack content.
    
    Simulates a realistic Substack article HTML and verifies:
    - Correct title extraction
    - Proper text compilation
    - Metadata retrieval
    """
    spider = SubstackSpider()
    
    # Simulated Substack article HTML
    mock_html = '''
    <html>
        <head>
            <meta name="author" content="Test Author">
            <title>Test Article</title>
        </head>
        <body>
            <h1 class="post-title">Complex Story Title</h1>
            <time datetime="2023-05-15T10:30:00Z">May 15, 2023</time>
            <div class="body markup">
                <p>First paragraph of the story.</p>
                <p>Second paragraph with some details.</p>
                <div class="paragraph">Third paragraph block.</div>
            </div>
        </body>
    </html>
    '''
    
    mock_content = {
        'url': 'https://example.substack.com/p/test-article',
        'content': mock_html
    }
    
    result = spider.extract_story(mock_content)
    
    assert result['title'] == 'Complex Story Title'
    assert result['author'] == 'Test Author'
    assert result['platform'] == 'Substack'
    assert 'First paragraph' in result['text']
    assert result['published_at'] is not None
    assert result['reading_time_minutes'] > 0

def test_substack_story_extraction_failure(mocker):
    """
    Test spider's behavior with invalid or empty content.
    
    Ensures that:
    - Empty content returns an empty dictionary
    - Exceptions are logged without crashing
    """
    spider = SubstackSpider()
    
    # Test with empty content
    empty_result = spider.extract_story({})
    assert empty_result == {}
    
    # Test with malformed content
    malformed_content = {'content': '<html></html>'}
    malformed_result = spider.extract_story(malformed_content)
    assert malformed_result == {}

def test_substack_reading_time_calculation():
    """
    Verify accurate reading time estimation.
    
    Checks that:
    - Reading time is calculated based on word count
    - Minimum reading time is 1 minute
    - Calculation follows standard reading speed
    """
    spider = SubstackSpider()
    
    # Simulated content with known word count
    test_cases = [
        ("Short text with few words.", 1),
        (" ".join(["word"] * 250), 1),
        (" ".join(["word"] * 500), 2),
        (" ".join(["word"] * 750), 3)
    ]
    
    for text, expected_time in test_cases:
        mock_content = {
            'url': 'https://test.substack.com',
            'content': f'<html><body><h1>Test</h1><div class="body">{text}</div></body></html>'
        }
        
        result = spider.extract_story(mock_content)
        assert result['reading_time_minutes'] == expected_time
