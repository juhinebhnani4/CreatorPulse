"""
Unit tests for YouTube scraper.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from ai_newsletter.scrapers.youtube_scraper import YouTubeScraper
from ai_newsletter.models.content import ContentItem


class TestYouTubeScraper:
    """Test cases for YouTubeScraper."""
    
    def test_init_with_api_key(self):
        """Test YouTubeScraper initialization with API key."""
        with patch('ai_newsletter.scrapers.youtube_scraper.build') as mock_build:
            mock_youtube = Mock()
            mock_build.return_value = mock_youtube
            
            scraper = YouTubeScraper(api_key="test_api_key")
            
            assert scraper.api_key == "test_api_key"
            assert scraper.youtube == mock_youtube
            mock_build.assert_called_once_with('youtube', 'v3', developerKey="test_api_key")
    
    def test_init_without_api_key(self):
        """Test YouTubeScraper initialization without API key."""
        with pytest.raises(ValueError, match="YouTube API key is required"):
            YouTubeScraper(api_key="")
    
    def test_init_with_invalid_api_key(self):
        """Test YouTubeScraper initialization with invalid API key."""
        with patch('ai_newsletter.scrapers.youtube_scraper.build') as mock_build:
            mock_build.side_effect = Exception("API error")
            
            with pytest.raises(Exception, match="API error"):
                YouTubeScraper(api_key="invalid_key")
    
    def test_parse_item(self):
        """Test parsing YouTube video data into ContentItem."""
        with patch('ai_newsletter.scrapers.youtube_scraper.build') as mock_build:
            mock_youtube = Mock()
            mock_build.return_value = mock_youtube
            
            scraper = YouTubeScraper(api_key="test_api_key")
            
            # Mock video data
            raw_item = {
                'id': 'test_video_id',
                'snippet': {
                    'title': 'Test Video Title',
                    'channelTitle': 'Test Channel',
                    'channelId': 'test_channel_id',
                    'description': 'Test video description',
                    'publishedAt': '2023-01-01T00:00:00Z',
                    'thumbnails': {
                        'high': {'url': 'https://example.com/thumb.jpg'}
                    },
                    'tags': ['AI', 'Machine Learning'],
                    'categoryId': '28'
                },
                'statistics': {
                    'viewCount': '1000',
                    'likeCount': '50',
                    'commentCount': '10'
                },
                'contentDetails': {
                    'duration': 'PT5M30S'
                }
            }
            
            item = scraper._parse_item(raw_item)
            
            assert isinstance(item, ContentItem)
            assert item.title == 'Test Video Title'
            assert item.source == 'youtube'
            assert item.author == 'Test Channel'
            assert item.score == 50  # like_count
            assert item.comments_count == 10
            assert item.views_count == 1000
            assert item.image_url == 'https://example.com/thumb.jpg'
            assert item.video_url == 'https://www.youtube.com/watch?v=test_video_id'
            assert 'AI' in item.tags
            assert 'Machine Learning' in item.tags
            assert item.metadata['video_id'] == 'test_video_id'
            assert item.metadata['channel_id'] == 'test_channel_id'
    
    def test_fetch_content_no_source(self):
        """Test fetch_content with no source specified."""
        with patch('ai_newsletter.scrapers.youtube_scraper.build') as mock_build:
            mock_youtube = Mock()
            mock_build.return_value = mock_youtube
            
            scraper = YouTubeScraper(api_key="test_api_key")
            
            result = scraper.fetch_content()
            
            assert result == []
    
    def test_fetch_content_channel_id(self):
        """Test fetch_content with channel_id."""
        with patch('ai_newsletter.scrapers.youtube_scraper.build') as mock_build:
            mock_youtube = Mock()
            mock_build.return_value = mock_youtube
            
            # Mock channel response
            mock_youtube.channels.return_value.list.return_value.execute.return_value = {
                'items': [{
                    'contentDetails': {
                        'relatedPlaylists': {
                            'uploads': 'test_playlist_id'
                        }
                    }
                }]
            }
            
            # Mock playlist response
            mock_youtube.playlistItems.return_value.list.return_value.execute.return_value = {
                'items': [{
                    'snippet': {
                        'resourceId': {
                            'videoId': 'test_video_id'
                        }
                    }
                }],
                'nextPageToken': None
            }
            
            # Mock videos response
            mock_youtube.videos.return_value.list.return_value.execute.return_value = {
                'items': [{
                    'id': 'test_video_id',
                    'snippet': {
                        'title': 'Test Video',
                        'channelTitle': 'Test Channel',
                        'channelId': 'test_channel_id',
                        'description': 'Test description',
                        'publishedAt': '2023-01-01T00:00:00Z',
                        'thumbnails': {'high': {'url': 'https://example.com/thumb.jpg'}},
                        'tags': ['AI'],
                        'categoryId': '28'
                    },
                    'statistics': {
                        'viewCount': '100',
                        'likeCount': '10',
                        'commentCount': '5'
                    },
                    'contentDetails': {
                        'duration': 'PT5M'
                    }
                }]
            }
            
            scraper = YouTubeScraper(api_key="test_api_key")
            
            result = scraper.fetch_content(channel_id="test_channel_id", limit=1)
            
            assert len(result) == 1
            assert result[0].title == 'Test Video'
            assert result[0].source == 'youtube'
    
    def test_fetch_content_search_query(self):
        """Test fetch_content with search query."""
        with patch('ai_newsletter.scrapers.youtube_scraper.build') as mock_build:
            mock_youtube = Mock()
            mock_build.return_value = mock_youtube
            
            # Mock search response
            mock_youtube.search.return_value.list.return_value.execute.return_value = {
                'items': [{
                    'id': {
                        'videoId': 'test_video_id'
                    }
                }]
            }
            
            # Mock videos response
            mock_youtube.videos.return_value.list.return_value.execute.return_value = {
                'items': [{
                    'id': 'test_video_id',
                    'snippet': {
                        'title': 'Test Search Video',
                        'channelTitle': 'Test Channel',
                        'channelId': 'test_channel_id',
                        'description': 'Test description',
                        'publishedAt': '2023-01-01T00:00:00Z',
                        'thumbnails': {'high': {'url': 'https://example.com/thumb.jpg'}},
                        'tags': ['AI'],
                        'categoryId': '28'
                    },
                    'statistics': {
                        'viewCount': '100',
                        'likeCount': '10',
                        'commentCount': '5'
                    },
                    'contentDetails': {
                        'duration': 'PT5M'
                    }
                }]
            }
            
            scraper = YouTubeScraper(api_key="test_api_key")
            
            result = scraper.fetch_content(search_query="AI news", limit=1)
            
            assert len(result) == 1
            assert result[0].title == 'Test Search Video'
            assert result[0].source == 'youtube'
    
    def test_fetch_content_api_error(self):
        """Test fetch_content with API error."""
        with patch('ai_newsletter.scrapers.youtube_scraper.build') as mock_build:
            mock_youtube = Mock()
            mock_build.return_value = mock_youtube
            
            # Mock API error
            from googleapiclient.errors import HttpError
            mock_youtube.channels.return_value.list.return_value.execute.side_effect = HttpError(
                resp=Mock(status=403), content=b'Forbidden'
            )
            
            scraper = YouTubeScraper(api_key="test_api_key")
            
            result = scraper.fetch_content(channel_id="test_channel_id")
            
            assert result == []
    
    def test_fetch_multiple_channels(self):
        """Test fetch_multiple_channels method."""
        with patch('ai_newsletter.scrapers.youtube_scraper.build') as mock_build:
            mock_youtube = Mock()
            mock_build.return_value = mock_youtube
            
            # Mock responses
            mock_youtube.channels.return_value.list.return_value.execute.return_value = {
                'items': [{
                    'contentDetails': {
                        'relatedPlaylists': {
                            'uploads': 'test_playlist_id'
                        }
                    }
                }]
            }
            
            mock_youtube.playlistItems.return_value.list.return_value.execute.return_value = {
                'items': [],
                'nextPageToken': None
            }
            
            mock_youtube.videos.return_value.list.return_value.execute.return_value = {
                'items': []
            }
            
            scraper = YouTubeScraper(api_key="test_api_key")
            
            result = scraper.fetch_multiple_channels(['channel1', 'channel2'], limit_per_channel=5)
            
            # Should call channels.list twice (once for each channel)
            assert mock_youtube.channels.return_value.list.call_count == 2
    
    def test_search_videos(self):
        """Test search_videos method."""
        with patch('ai_newsletter.scrapers.youtube_scraper.build') as mock_build:
            mock_youtube = Mock()
            mock_build.return_value = mock_youtube
            
            # Mock search response
            mock_youtube.search.return_value.list.return_value.execute.return_value = {
                'items': [{
                    'id': {
                        'videoId': 'test_video_id'
                    }
                }]
            }
            
            # Mock videos response
            mock_youtube.videos.return_value.list.return_value.execute.return_value = {
                'items': [{
                    'id': 'test_video_id',
                    'snippet': {
                        'title': 'Test Search Video',
                        'channelTitle': 'Test Channel',
                        'channelId': 'test_channel_id',
                        'description': 'Test description',
                        'publishedAt': '2023-01-01T00:00:00Z',
                        'thumbnails': {'high': {'url': 'https://example.com/thumb.jpg'}},
                        'tags': ['AI'],
                        'categoryId': '28'
                    },
                    'statistics': {
                        'viewCount': '100',
                        'likeCount': '10',
                        'commentCount': '5'
                    },
                    'contentDetails': {
                        'duration': 'PT5M'
                    }
                }]
            }
            
            scraper = YouTubeScraper(api_key="test_api_key")
            
            result = scraper.search_videos("AI news", limit=1)
            
            assert len(result) == 1
            assert result[0].title == 'Test Search Video'
            assert result[0].source == 'youtube'








