"""
Unit tests for newsletter generator.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from ai_newsletter.generators.newsletter_generator import NewsletterGenerator
from ai_newsletter.models.content import ContentItem


class TestNewsletterGenerator:
    """Test cases for NewsletterGenerator."""
    
    def test_init_with_api_key(self):
        """Test NewsletterGenerator initialization with API key."""
        with patch('ai_newsletter.generators.newsletter_generator.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            generator = NewsletterGenerator(api_key="test_api_key")
            
            assert generator.api_key == "test_api_key"
            assert generator.client == mock_client
            mock_openai.assert_called_once_with(api_key="test_api_key")
    
    def test_init_without_api_key(self):
        """Test NewsletterGenerator initialization without API key."""
        with pytest.raises(ValueError, match="OpenAI API key not provided"):
            NewsletterGenerator(api_key="")
    
    def test_init_with_invalid_api_key(self):
        """Test NewsletterGenerator initialization with invalid API key."""
        with patch('ai_newsletter.generators.newsletter_generator.OpenAI') as mock_openai:
            mock_openai.side_effect = Exception("API error")
            
            with pytest.raises(Exception, match="API error"):
                NewsletterGenerator(api_key="invalid_key")
    
    def test_build_prompt(self):
        """Test building prompt for newsletter generation."""
        with patch('ai_newsletter.generators.newsletter_generator.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            generator = NewsletterGenerator(api_key="test_api_key")
            
            # Create test content items
            items = [
                ContentItem(
                    title="Test Article 1",
                    source="reddit",
                    source_url="https://reddit.com/test1",
                    created_at=datetime.now(),
                    content="Test content 1",
                    summary="Test summary 1",
                    author="Test Author 1",
                    score=100
                ),
                ContentItem(
                    title="Test Article 2",
                    source="youtube",
                    source_url="https://youtube.com/test2",
                    created_at=datetime.now(),
                    content="Test content 2",
                    summary="Test summary 2",
                    author="Test Author 2",
                    score=50,
                    views_count=1000
                )
            ]
            
            prompt = generator._build_prompt(items, "Test Newsletter", 2)
            
            assert "Test Article 1" in prompt
            assert "Test Article 2" in prompt
            assert "Test Newsletter" in prompt
            assert "reddit" in prompt
            assert "youtube" in prompt
            assert "Test Author 1" in prompt
            assert "Test Author 2" in prompt
    
    def test_format_html(self):
        """Test HTML formatting."""
        with patch('ai_newsletter.generators.newsletter_generator.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            generator = NewsletterGenerator(api_key="test_api_key")
            
            raw_content = """
            <h2>Introduction</h2>
            <p>Welcome to our newsletter!</p>
            
            <h2>Top Stories</h2>
            <p>Here are the top stories...</p>
            
            <h2>Conclusion</h2>
            <p>Thanks for reading!</p>
            """
            
            html = generator._format_html(raw_content, "Test Newsletter")
            
            assert "Test Newsletter" in html
            assert "Introduction" in html
            assert "Top Stories" in html
            assert "Conclusion" in html
            assert "<html>" in html
            assert "<body>" in html
    
    def test_generate_newsletter(self):
        """Test newsletter generation."""
        with patch('ai_newsletter.generators.newsletter_generator.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # Mock OpenAI response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = """
            <h2>Introduction</h2>
            <p>Welcome to our newsletter!</p>
            
            <h2>Top Stories</h2>
            <p>Here are the top stories...</p>
            
            <h2>Conclusion</h2>
            <p>Thanks for reading!</p>
            """
            mock_client.chat.completions.create.return_value = mock_response
            
            generator = NewsletterGenerator(api_key="test_api_key")
            
            # Create test content items
            items = [
                ContentItem(
                    title="Test Article",
                    source="reddit",
                    source_url="https://reddit.com/test",
                    created_at=datetime.now(),
                    content="Test content",
                    summary="Test summary",
                    author="Test Author",
                    score=100
                )
            ]
            
            newsletter = generator.generate_newsletter(items, "Test Newsletter", 1)
            
            assert "Test Newsletter" in newsletter
            assert "Introduction" in newsletter
            assert "Top Stories" in newsletter
            assert "Conclusion" in newsletter
            assert "<html>" in newsletter
            assert "<body>" in newsletter
    
    def test_generate_newsletter_no_items(self):
        """Test newsletter generation with no items."""
        with patch('ai_newsletter.generators.newsletter_generator.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            generator = NewsletterGenerator(api_key="test_api_key")
            
            newsletter = generator.generate_newsletter([], "Test Newsletter", 1)
            
            assert "No content available" in newsletter
            assert "<html>" in newsletter
            assert "<body>" in newsletter
    
    def test_generate_newsletter_api_error(self):
        """Test newsletter generation with API error."""
        with patch('ai_newsletter.generators.newsletter_generator.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # Mock API error
            import openai
            mock_client.chat.completions.create.side_effect = openai.APIError("API error")
            
            generator = NewsletterGenerator(api_key="test_api_key")
            
            items = [
                ContentItem(
                    title="Test Article",
                    source="reddit",
                    source_url="https://reddit.com/test",
                    created_at=datetime.now(),
                    content="Test content",
                    summary="Test summary",
                    author="Test Author",
                    score=100
                )
            ]
            
            with pytest.raises(openai.APIError, match="API error"):
                generator.generate_newsletter(items, "Test Newsletter", 1)
    
    def test_generate_newsletter_template_error(self):
        """Test newsletter generation with template error."""
        with patch('ai_newsletter.generators.newsletter_generator.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # Mock OpenAI response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test content"
            mock_client.chat.completions.create.return_value = mock_response
            
            generator = NewsletterGenerator(api_key="test_api_key")
            
            # Mock template error
            with patch.object(generator.env, 'get_template') as mock_template:
                mock_template.side_effect = Exception("Template error")
                
                items = [
                    ContentItem(
                        title="Test Article",
                        source="reddit",
                        source_url="https://reddit.com/test",
                        created_at=datetime.now(),
                        content="Test content",
                        summary="Test summary",
                        author="Test Author",
                        score=100
                    )
                ]
                
                newsletter = generator.generate_newsletter(items, "Test Newsletter", 1)
                
                # Should fallback to basic HTML
                assert "Test Newsletter" in newsletter
                assert "<html>" in newsletter
                assert "<body>" in newsletter
                assert "Test content" in newsletter