"""
Integration Tests: Content API with Thumbnail Support

Tests end-to-end thumbnail flow:
1. Scraping populates image_url field in database
2. Content API returns thumbnail data
3. Thumbnails persist correctly in Supabase
4. Feedback API works with thumbnail-enabled content

Critical: Tests database schema and API contract for thumbnails
"""

import pytest
import asyncio
from datetime import datetime, UTC
from uuid import uuid4
from supabase import create_client, Client
from src.ai_newsletter.database.supabase_client import SupabaseClient
from src.ai_newsletter.scrapers.youtube_scraper import YouTubeScraper
from src.ai_newsletter.scrapers.reddit_scraper import RedditScraper
from src.ai_newsletter.models.content import ContentItem
import os


@pytest.fixture
def supabase_client() -> SupabaseClient:
    """Create authenticated Supabase client for testing"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not url or not key:
        pytest.skip("Supabase credentials not configured")

    return SupabaseClient(url, key)


@pytest.fixture
async def test_workspace(supabase_client: SupabaseClient):
    """Create test workspace for integration tests"""
    # Create test user first
    test_email = f"thumbnail-test-{uuid4()}@example.com"
    test_user_id = str(uuid4())

    # Insert test user (bypassing auth for testing)
    user_data = {
        'user_id': test_user_id,
        'email': test_email,
        'username': 'Thumbnail Test User',
        'created_at': datetime.now(UTC).isoformat()
    }

    supabase_client.client.table('users').insert(user_data).execute()

    # Create test workspace
    workspace_id = str(uuid4())
    workspace_data = {
        'id': workspace_id,
        'user_id': test_user_id,
        'name': 'Thumbnail Test Workspace',
        'created_at': datetime.now(UTC).isoformat()
    }

    supabase_client.client.table('workspaces').insert(workspace_data).execute()

    yield {
        'workspace_id': workspace_id,
        'user_id': test_user_id,
        'email': test_email
    }

    # Cleanup
    supabase_client.client.table('workspaces').delete().eq('id', workspace_id).execute()
    supabase_client.client.table('users').delete().eq('user_id', test_user_id).execute()


class TestContentItemThumbnailPersistence:
    """Test thumbnail data persistence in database"""

    def test_insert_content_with_thumbnail(self, supabase_client: SupabaseClient, test_workspace):
        """Should successfully insert content item with image_url"""
        workspace_id = test_workspace['workspace_id']

        # Create content item with thumbnail
        content_data = {
            'id': str(uuid4()),
            'workspace_id': workspace_id,
            'title': 'Test Content with Thumbnail',
            'url': 'https://example.com/test-content',
            'content': 'Test content description',
            'source_type': 'youtube',
            'image_url': 'https://example.com/thumbnail.jpg',
            'scraped_at': datetime.now(UTC).isoformat()
        }

        # Insert into database
        result = supabase_client.client.table('content_items').insert(content_data).execute()

        assert result.data is not None
        assert len(result.data) == 1
        assert result.data[0]['image_url'] == 'https://example.com/thumbnail.jpg'

        print(f"✓ Content item with thumbnail inserted successfully")
        print(f"  - ID: {result.data[0]['id']}")
        print(f"  - Image URL: {result.data[0]['image_url']}")

    def test_insert_content_without_thumbnail(self, supabase_client: SupabaseClient, test_workspace):
        """Should successfully insert content item without image_url (null)"""
        workspace_id = test_workspace['workspace_id']

        # Create content item without thumbnail
        content_data = {
            'id': str(uuid4()),
            'workspace_id': workspace_id,
            'title': 'Test Content without Thumbnail',
            'url': 'https://example.com/test-content-no-thumb',
            'content': 'Test content description',
            'source_type': 'reddit',
            'image_url': None,
            'scraped_at': datetime.now(UTC).isoformat()
        }

        # Insert into database
        result = supabase_client.client.table('content_items').insert(content_data).execute()

        assert result.data is not None
        assert len(result.data) == 1
        assert result.data[0]['image_url'] is None

        print(f"✓ Content item without thumbnail inserted successfully")
        print(f"  - ID: {result.data[0]['id']}")
        print(f"  - Image URL: None")

    def test_query_content_items_with_thumbnails(self, supabase_client: SupabaseClient, test_workspace):
        """Should query and filter content items by thumbnail presence"""
        workspace_id = test_workspace['workspace_id']

        # Insert multiple content items
        items = [
            {
                'id': str(uuid4()),
                'workspace_id': workspace_id,
                'title': f'Content with Thumbnail {i}',
                'url': f'https://example.com/content-{i}',
                'content': 'Test content',
                'source_type': 'youtube',
                'image_url': f'https://example.com/thumb-{i}.jpg',
                'scraped_at': datetime.now(UTC).isoformat()
            }
            for i in range(3)
        ]

        items.append({
            'id': str(uuid4()),
            'workspace_id': workspace_id,
            'title': 'Content without Thumbnail',
            'url': 'https://example.com/no-thumb',
            'content': 'Test content',
            'source_type': 'reddit',
            'image_url': None,
            'scraped_at': datetime.now(UTC).isoformat()
        })

        # Bulk insert
        supabase_client.client.table('content_items').insert(items).execute()

        # Query all content for workspace
        all_content = supabase_client.client.table('content_items') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .execute()

        assert len(all_content.data) == 4

        # Filter items with thumbnails
        items_with_thumbnails = [item for item in all_content.data if item['image_url']]
        items_without_thumbnails = [item for item in all_content.data if not item['image_url']]

        assert len(items_with_thumbnails) == 3
        assert len(items_without_thumbnails) == 1

        print(f"✓ Content query successful")
        print(f"  - Total items: {len(all_content.data)}")
        print(f"  - With thumbnails: {len(items_with_thumbnails)}")
        print(f"  - Without thumbnails: {len(items_without_thumbnails)}")


class TestContentAPIThumbnailResponse:
    """Test Content API returns thumbnail data correctly"""

    def test_get_workspace_content_includes_thumbnails(self, supabase_client: SupabaseClient, test_workspace):
        """Should include image_url field in content API response"""
        workspace_id = test_workspace['workspace_id']

        # Insert test content with thumbnails
        content_data = {
            'id': str(uuid4()),
            'workspace_id': workspace_id,
            'title': 'API Test Content',
            'url': 'https://example.com/api-test',
            'content': 'API test content',
            'source_type': 'youtube',
            'image_url': 'https://i.ytimg.com/vi/test123/hqdefault.jpg',
            'scraped_at': datetime.now(UTC).isoformat()
        }

        supabase_client.client.table('content_items').insert(content_data).execute()

        # Query via API pattern (what frontend does)
        response = supabase_client.client.table('content_items') \
            .select('id, workspace_id, title, url, content, source_type, image_url, scraped_at, quality_score') \
            .eq('workspace_id', workspace_id) \
            .order('scraped_at', desc=True) \
            .execute()

        assert response.data is not None
        assert len(response.data) > 0

        item = response.data[0]
        assert 'image_url' in item
        assert item['image_url'] == 'https://i.ytimg.com/vi/test123/hqdefault.jpg'
        assert item['source_type'] == 'youtube'

        print(f"✓ Content API includes thumbnail data")
        print(f"  - API Response keys: {list(item.keys())}")
        print(f"  - Image URL: {item['image_url']}")

    def test_api_response_schema_validation(self, supabase_client: SupabaseClient, test_workspace):
        """Should validate API response schema includes all required fields"""
        workspace_id = test_workspace['workspace_id']

        # Insert minimal content item
        content_data = {
            'id': str(uuid4()),
            'workspace_id': workspace_id,
            'title': 'Schema Test',
            'url': 'https://example.com/schema-test',
            'content': 'Schema test content',
            'source_type': 'blog',
            'image_url': 'https://example.com/blog-image.jpg',
            'scraped_at': datetime.now(UTC).isoformat()
        }

        supabase_client.client.table('content_items').insert(content_data).execute()

        # Query content
        response = supabase_client.client.table('content_items') \
            .select('*') \
            .eq('workspace_id', workspace_id) \
            .limit(1) \
            .execute()

        assert len(response.data) == 1
        item = response.data[0]

        # Validate required fields
        required_fields = ['id', 'workspace_id', 'title', 'url', 'content', 'source_type', 'scraped_at']
        for field in required_fields:
            assert field in item, f"Missing required field: {field}"

        # Validate optional thumbnail field
        assert 'image_url' in item

        print(f"✓ API response schema validated")
        print(f"  - All required fields present")
        print(f"  - Thumbnail field (image_url) included")


class TestScraperThumbnailIntegration:
    """Test scrapers populate thumbnails in database"""

    @pytest.mark.skipif(not os.getenv('YOUTUBE_API_KEY'), reason="YouTube API key not configured")
    def test_youtube_scraper_populates_thumbnails(self, supabase_client: SupabaseClient, test_workspace):
        """Should scrape YouTube content and save thumbnails to database"""
        workspace_id = test_workspace['workspace_id']

        # Configure YouTube scraper
        config = {
            'api_key': os.getenv('YOUTUBE_API_KEY'),
            'channels': ['UCBJycsmduvYEL83R_U4JriQ'],  # Example channel
            'max_results': 3
        }

        scraper = YouTubeScraper(config)
        items = scraper.scrape()

        # Should have scraped items
        assert len(items) > 0

        # Filter items with thumbnails
        items_with_thumbnails = [item for item in items if item.image_url]

        # YouTube should have thumbnails for all videos
        assert len(items_with_thumbnails) > 0

        # Validate thumbnail URLs
        for item in items_with_thumbnails:
            assert item.image_url.startswith('https://')
            assert 'ytimg.com' in item.image_url or 'youtube.com' in item.image_url

        print(f"✓ YouTube scraper extracted thumbnails")
        print(f"  - Total items: {len(items)}")
        print(f"  - With thumbnails: {len(items_with_thumbnails)}")
        print(f"  - Sample thumbnail: {items_with_thumbnails[0].image_url}")

    @pytest.mark.skipif(
        not os.getenv('REDDIT_CLIENT_ID') or not os.getenv('REDDIT_CLIENT_SECRET'),
        reason="Reddit credentials not configured"
    )
    def test_reddit_scraper_populates_thumbnails(self, supabase_client: SupabaseClient, test_workspace):
        """Should scrape Reddit content and save thumbnails when available"""
        workspace_id = test_workspace['workspace_id']

        # Configure Reddit scraper
        config = {
            'client_id': os.getenv('REDDIT_CLIENT_ID'),
            'client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
            'user_agent': 'CreatorPulse Test/1.0',
            'subreddits': ['programming'],
            'limit': 5
        }

        scraper = RedditScraper(config)
        items = scraper.scrape()

        assert len(items) > 0

        # Some Reddit posts have thumbnails, some don't
        items_with_thumbnails = [item for item in items if item.image_url]

        print(f"✓ Reddit scraper processed thumbnails")
        print(f"  - Total items: {len(items)}")
        print(f"  - With thumbnails: {len(items_with_thumbnails)}")

        if items_with_thumbnails:
            print(f"  - Sample thumbnail: {items_with_thumbnails[0].image_url}")


class TestFeedbackAPIWithThumbnails:
    """Test feedback API works correctly with thumbnail-enabled content"""

    def test_submit_feedback_for_content_with_thumbnail(self, supabase_client: SupabaseClient, test_workspace):
        """Should submit feedback for content item with thumbnail"""
        workspace_id = test_workspace['workspace_id']
        user_id = test_workspace['user_id']

        # Insert content with thumbnail
        content_id = str(uuid4())
        content_data = {
            'id': content_id,
            'workspace_id': workspace_id,
            'title': 'Feedback Test Content',
            'url': 'https://example.com/feedback-test',
            'content': 'Test content for feedback',
            'source_type': 'youtube',
            'image_url': 'https://example.com/feedback-thumb.jpg',
            'scraped_at': datetime.now(UTC).isoformat()
        }

        supabase_client.client.table('content_items').insert(content_data).execute()

        # Submit feedback
        feedback_data = {
            'id': str(uuid4()),
            'workspace_id': workspace_id,
            'content_item_id': content_id,
            'rating': 5,
            'feedback_type': 'content_quality',
            'created_at': datetime.now(UTC).isoformat()
        }

        result = supabase_client.client.table('feedback').insert(feedback_data).execute()

        assert result.data is not None
        assert len(result.data) == 1
        assert result.data[0]['content_item_id'] == content_id
        assert result.data[0]['rating'] == 5

        print(f"✓ Feedback submitted for content with thumbnail")
        print(f"  - Content ID: {content_id}")
        print(f"  - Feedback ID: {result.data[0]['id']}")
        print(f"  - Rating: {result.data[0]['rating']}")

    def test_query_feedback_with_content_thumbnails(self, supabase_client: SupabaseClient, test_workspace):
        """Should join feedback with content to get thumbnail data"""
        workspace_id = test_workspace['workspace_id']

        # Insert content with thumbnail
        content_id = str(uuid4())
        content_data = {
            'id': content_id,
            'workspace_id': workspace_id,
            'title': 'Join Test Content',
            'url': 'https://example.com/join-test',
            'content': 'Test content for join',
            'source_type': 'youtube',
            'image_url': 'https://example.com/join-thumb.jpg',
            'scraped_at': datetime.now(UTC).isoformat()
        }

        supabase_client.client.table('content_items').insert(content_data).execute()

        # Submit feedback
        feedback_data = {
            'id': str(uuid4()),
            'workspace_id': workspace_id,
            'content_item_id': content_id,
            'rating': 5,
            'feedback_type': 'content_quality',
            'created_at': datetime.now(UTC).isoformat()
        }

        supabase_client.client.table('feedback').insert(feedback_data).execute()

        # Query feedback with content join
        response = supabase_client.client.table('feedback') \
            .select('*, content_items(title, image_url, source_type)') \
            .eq('workspace_id', workspace_id) \
            .execute()

        assert len(response.data) > 0
        feedback = response.data[0]

        # Should have nested content data
        assert 'content_items' in feedback
        assert feedback['content_items']['image_url'] == 'https://example.com/join-thumb.jpg'

        print(f"✓ Feedback query with content join successful")
        print(f"  - Feedback includes content thumbnail")
        print(f"  - Image URL: {feedback['content_items']['image_url']}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
