#!/usr/bin/env python3
"""
CreatorPulse Example Script

This script demonstrates how to use CreatorPulse to generate and send newsletters
programmatically without the Streamlit UI.

Usage:
    python examples/creatorpulse_example.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_newsletter.orchestrator import NewsletterPipeline
from ai_newsletter.config.settings import get_settings
from ai_newsletter.scrapers.youtube_scraper import YouTubeScraper
from ai_newsletter.generators import NewsletterGenerator
from ai_newsletter.delivery import EmailSender
from ai_newsletter.scheduler import DailyScheduler


def main():
    """Main example function."""
    print("🚀 CreatorPulse Example Script")
    print("=" * 50)
    
    # Load settings
    settings = get_settings()
    print(f"📋 Loaded settings: {settings.app_name}")
    
    # Example 1: Individual Component Usage
    print("\n1️⃣ Individual Component Examples")
    print("-" * 30)
    
    # YouTube Scraper Example
    if settings.youtube.api_key:
        print("📺 Testing YouTube Scraper...")
        try:
            youtube_scraper = YouTubeScraper(api_key=settings.youtube.api_key)
            
            # Search for AI videos
            videos = youtube_scraper.search_videos("AI news", limit=5)
            print(f"   ✅ Found {len(videos)} videos")
            
            if videos:
                print(f"   📹 Latest video: {videos[0].title}")
        except Exception as e:
            print(f"   ❌ YouTube error: {e}")
    else:
        print("   ⚠️ YouTube API key not configured")
    
    # Newsletter Generator Example
    if settings.newsletter.openai_api_key:
        print("\n📝 Testing Newsletter Generator...")
        try:
            generator = NewsletterGenerator(
                config=settings.newsletter
            )
            print("   ✅ Newsletter generator initialized")
        except Exception as e:
            print(f"   ❌ Newsletter generator error: {e}")
    else:
        print("   ⚠️ OpenAI API key not configured")
    
    # Email Sender Example
    if settings.email.from_email:
        print("\n📧 Testing Email Sender...")
        try:
            email_sender = EmailSender(config=settings.email)
            status = email_sender.get_config_status()
            print(f"   ✅ Email sender configured: {status['provider']}")
            print(f"   🔗 Connection test: {'✅ OK' if status['connection_test'] else '❌ Failed'}")
        except Exception as e:
            print(f"   ❌ Email sender error: {e}")
    else:
        print("   ⚠️ Email configuration not complete")
    
    # Example 2: Complete Pipeline
    print("\n2️⃣ Complete Pipeline Example")
    print("-" * 30)
    
    try:
        pipeline = NewsletterPipeline(settings)
        status = pipeline.get_pipeline_status()
        
        print(f"📊 Pipeline Status:")
        print(f"   Scrapers: {status['scrapers_configured']}")
        print(f"   Generator: {'✅' if status['newsletter_generator_available'] else '❌'}")
        print(f"   Email: {'✅' if status['email_sender_available'] else '❌'}")
        
        # Run pipeline preview
        print("\n👁️ Generating Pipeline Preview...")
        preview = pipeline.preview_newsletter(max_items_per_source=5, max_total_items=15)
        
        if preview:
            print(f"   ✅ Preview generated with {preview['items_count']} items")
            print(f"   📊 Sources: {', '.join(preview['sources'])}")
            print(f"   ⏰ Generated at: {preview['generated_at']}")
        else:
            print("   ⚠️ No preview available - check configuration")
            
    except Exception as e:
        print(f"   ❌ Pipeline error: {e}")
    
    # Example 3: Scheduler Example
    print("\n3️⃣ Scheduler Example")
    print("-" * 30)
    
    if settings.scheduler.enabled:
        print("⏰ Testing Scheduler...")
        try:
            scheduler = DailyScheduler(config=settings.scheduler)
            
            # Create a simple callback function
            def test_callback():
                print("   📧 Newsletter job executed!")
                return True
            
            # Schedule a test job
            success = scheduler.schedule_newsletter_job(
                test_callback,
                schedule_time="09:00",
                timezone="UTC"
            )
            
            if success:
                print("   ✅ Test job scheduled successfully")
                scheduler_status = scheduler.get_scheduler_status()
                print(f"   📊 Scheduler status: {scheduler_status['running']}")
            else:
                print("   ❌ Failed to schedule job")
                
        except Exception as e:
            print(f"   ❌ Scheduler error: {e}")
    else:
        print("   ⚠️ Scheduler is disabled")
    
    # Example 4: Configuration Check
    print("\n4️⃣ Configuration Check")
    print("-" * 30)
    
    config_status = {
        "YouTube API": bool(settings.youtube.api_key),
        "OpenAI API": bool(settings.newsletter.openai_api_key),
        "Email Config": bool(settings.email.from_email),
        "Scheduler": settings.scheduler.enabled,
    }
    
    for service, configured in config_status.items():
        status_icon = "✅" if configured else "❌"
        print(f"   {status_icon} {service}: {'Configured' if configured else 'Not configured'}")
    
    # Summary
    print("\n📋 Summary")
    print("-" * 30)
    
    configured_services = sum(config_status.values())
    total_services = len(config_status)
    
    print(f"🎯 Configuration: {configured_services}/{total_services} services configured")
    
    if configured_services == total_services:
        print("🎉 All services configured! CreatorPulse is ready to use.")
        print("\n💡 Next steps:")
        print("   1. Run the Streamlit app: streamlit run src/streamlit_app.py")
        print("   2. Configure your content sources in the UI")
        print("   3. Generate and send your first newsletter!")
    else:
        print("⚠️ Some services need configuration. Check the config.example.json file.")
        print("\n💡 Required environment variables:")
        print("   - YOUTUBE_API_KEY")
        print("   - OPENAI_API_KEY")
        print("   - SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD, FROM_EMAIL")


if __name__ == "__main__":
    main()
