#!/usr/bin/env python3
"""
Newsletter Generation Example Script

This script demonstrates how to generate newsletters using CreatorPulse
without sending them - perfect for testing and previewing content.

Usage:
    python examples/generate_newsletter.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_newsletter.orchestrator import NewsletterPipeline
from ai_newsletter.config.settings import get_settings
from ai_newsletter.scrapers.youtube_scraper import YouTubeScraper
from ai_newsletter.scrapers.reddit_scraper import RedditScraper
from ai_newsletter.generators import NewsletterGenerator
from ai_newsletter.models.content import ContentItem
from datetime import datetime, timedelta


def generate_sample_content():
    """Generate sample content for testing."""
    print("📝 Generating sample content...")
    
    # Create sample content items
    sample_items = [
        ContentItem(
            title="AI Breakthrough: New Language Model Achieves Human-Level Performance",
            source="reddit",
            source_url="https://reddit.com/r/AI_Agents/comments/sample1",
            created_at=datetime.now() - timedelta(hours=2),
            content="Researchers have developed a new language model that demonstrates human-level performance across multiple benchmarks...",
            summary="Revolutionary AI model shows unprecedented capabilities in natural language understanding and generation.",
            author="AI_Researcher",
            score=1250,
            comments_count=89,
            views_count=15420,
            tags=["AI", "Machine Learning", "Breakthrough", "Research"]
        ),
        ContentItem(
            title="Building AI Agents: A Complete Tutorial Series",
            source="youtube",
            source_url="https://youtube.com/watch?v=sample2",
            created_at=datetime.now() - timedelta(hours=5),
            content="In this comprehensive tutorial series, we'll explore how to build intelligent AI agents from scratch...",
            summary="Step-by-step guide to creating AI agents with practical examples and real-world applications.",
            author="TechTutorials",
            score=890,
            comments_count=45,
            views_count=12500,
            tags=["Tutorial", "AI Agents", "Programming", "Education"]
        ),
        ContentItem(
            title="The Future of Work: How AI Will Transform Every Industry",
            source="rss",
            source_url="https://example.com/blog/future-work-ai",
            created_at=datetime.now() - timedelta(hours=8),
            content="Artificial Intelligence is poised to revolutionize how we work across every sector...",
            summary="Comprehensive analysis of AI's impact on employment, productivity, and business models.",
            author="FutureInsights",
            score=650,
            comments_count=23,
            views_count=8900,
            tags=["Future of Work", "AI Impact", "Business", "Analysis"]
        ),
        ContentItem(
            title="Open Source AI Tools You Should Know About",
            source="reddit",
            source_url="https://reddit.com/r/MachineLearning/comments/sample3",
            created_at=datetime.now() - timedelta(hours=12),
            content="Here's a curated list of the most useful open-source AI tools for developers and researchers...",
            summary="Essential open-source AI tools and libraries for building intelligent applications.",
            author="OpenSourceDev",
            score=420,
            comments_count=67,
            views_count=5600,
            tags=["Open Source", "AI Tools", "Development", "Resources"]
        ),
        ContentItem(
            title="Machine Learning Ethics: Building Responsible AI Systems",
            source="youtube",
            source_url="https://youtube.com/watch?v=sample4",
            created_at=datetime.now() - timedelta(hours=18),
            content="As AI systems become more powerful, ensuring they are ethical and responsible is crucial...",
            summary="Exploring the ethical considerations and best practices for developing responsible AI systems.",
            author="EthicsInTech",
            score=320,
            comments_count=28,
            views_count=4200,
            tags=["Ethics", "Responsible AI", "Machine Learning", "Best Practices"]
        )
    ]
    
    print(f"✅ Generated {len(sample_items)} sample content items")
    return sample_items


def test_newsletter_generation():
    """Test newsletter generation with sample content."""
    print("\n📧 Testing Newsletter Generation")
    print("-" * 40)
    
    # Load settings
    settings = get_settings()
    
    if not settings.newsletter.openai_api_key:
        print("❌ OpenAI API key not configured")
        print("   Set OPENAI_API_KEY environment variable or update config.json")
        return None
    
    try:
        # Initialize newsletter generator
        generator = NewsletterGenerator(
            api_key=settings.newsletter.openai_api_key,
            config=settings.newsletter
        )
        print("✅ Newsletter generator initialized")
        
        # Generate sample content
        sample_items = generate_sample_content()
        
        # Generate newsletter
        print("🤖 Generating newsletter with AI...")
        newsletter_html = generator.generate_newsletter(
            sample_items,
            title="AI Weekly Digest",
            intro="Welcome to this week's AI newsletter! Here are the most exciting developments in artificial intelligence.",
            footer="Thanks for reading! Stay tuned for more AI insights next week."
        )
        
        print("✅ Newsletter generated successfully")
        
        # Save newsletter to file
        output_file = Path("generated_newsletter.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(newsletter_html)
        
        print(f"💾 Newsletter saved to: {output_file}")
        
        # Generate preview data
        preview = generator.preview_newsletter(sample_items)
        print(f"📊 Preview stats:")
        print(f"   - Items: {preview['item_count']}")
        print(f"   - Generated at: {preview['generated_at']}")
        print(f"   - Model: {preview['config']['model']}")
        print(f"   - Temperature: {preview['config']['temperature']}")
        
        return newsletter_html
        
    except Exception as e:
        print(f"❌ Newsletter generation failed: {e}")
        return None


def test_pipeline_preview():
    """Test the complete pipeline preview."""
    print("\n🔄 Testing Complete Pipeline Preview")
    print("-" * 40)
    
    try:
        # Initialize pipeline
        settings = get_settings()
        pipeline = NewsletterPipeline(settings)
        
        # Get pipeline status
        status = pipeline.get_pipeline_status()
        print(f"📊 Pipeline Status:")
        print(f"   - Scrapers configured: {status['scrapers_configured']}")
        print(f"   - Scraper types: {', '.join(status['scraper_types'])}")
        print(f"   - Newsletter generator: {'✅' if status['newsletter_generator_available'] else '❌'}")
        print(f"   - Email sender: {'✅' if status['email_sender_available'] else '❌'}")
        
        # Generate preview
        print("\n👁️ Generating pipeline preview...")
        preview = pipeline.preview_newsletter(
            max_items_per_source=3,
            max_total_items=10
        )
        
        if preview:
            print(f"✅ Preview generated successfully")
            print(f"   - Items: {preview['items_count']}")
            print(f"   - Sources: {', '.join(preview['sources'])}")
            print(f"   - Generated at: {preview['generated_at']}")
            
            # Save preview
            output_file = Path("pipeline_preview.html")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(preview['html'])
            print(f"💾 Preview saved to: {output_file}")
            
        else:
            print("⚠️ No preview available - check configuration")
            
    except Exception as e:
        print(f"❌ Pipeline preview failed: {e}")


def test_individual_scrapers():
    """Test individual scrapers."""
    print("\n🔍 Testing Individual Scrapers")
    print("-" * 40)
    
    settings = get_settings()
    
    # Test Reddit scraper
    if settings.reddit.enabled and settings.reddit.subreddits:
        print("📱 Testing Reddit Scraper...")
        try:
            reddit_scraper = RedditScraper()
            items = reddit_scraper.fetch_multiple_subreddits(
                settings.reddit.subreddits[:2],  # Test first 2 subreddits
                limit=3
            )
            print(f"   ✅ Found {len(items)} Reddit posts")
            if items:
                print(f"   📝 Latest: {items[0].title[:50]}...")
        except Exception as e:
            print(f"   ❌ Reddit error: {e}")
    
    # Test YouTube scraper
    if settings.youtube.enabled and settings.youtube.api_key:
        print("📺 Testing YouTube Scraper...")
        try:
            youtube_scraper = YouTubeScraper(api_key=settings.youtube.api_key)
            
            # Test search
            if settings.youtube.search_queries:
                items = youtube_scraper.search_videos(
                    settings.youtube.search_queries[0],
                    limit=3
                )
                print(f"   ✅ Found {len(items)} YouTube videos")
                if items:
                    print(f"   🎥 Latest: {items[0].title[:50]}...")
            
        except Exception as e:
            print(f"   ❌ YouTube error: {e}")
    else:
        print("   ⚠️ YouTube API key not configured")


def main():
    """Main example function."""
    print("🚀 CreatorPulse Newsletter Generation Example")
    print("=" * 60)
    
    # Test individual scrapers
    test_individual_scrapers()
    
    # Test newsletter generation
    newsletter_html = test_newsletter_generation()
    
    # Test pipeline preview
    test_pipeline_preview()
    
    # Summary
    print("\n📋 Summary")
    print("-" * 30)
    
    if newsletter_html:
        print("🎉 Newsletter generation successful!")
        print("\n💡 Next steps:")
        print("   1. Open generated_newsletter.html in your browser")
        print("   2. Review the generated content")
        print("   3. Customize the template if needed")
        print("   4. Test email sending with examples/send_newsletter.py")
    else:
        print("⚠️ Newsletter generation failed")
        print("\n💡 Troubleshooting:")
        print("   1. Check your OpenAI API key configuration")
        print("   2. Verify internet connection")
        print("   3. Review error messages above")
    
    print("\n📚 More examples:")
    print("   - examples/send_newsletter.py - Send newsletters via email")
    print("   - examples/scheduled_newsletter.py - Schedule automated newsletters")
    print("   - examples/creatorpulse_example.py - Complete CreatorPulse demo")


if __name__ == "__main__":
    main()
