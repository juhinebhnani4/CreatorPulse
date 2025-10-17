#!/usr/bin/env python3
"""
Scheduled Newsletter Example Script

This script demonstrates how to set up automated newsletter delivery
using CreatorPulse's scheduling system.

Usage:
    python examples/scheduled_newsletter.py
"""

import sys
from pathlib import Path
import time
import signal
import threading

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_newsletter.orchestrator import NewsletterPipeline
from ai_newsletter.scheduler import DailyScheduler
from ai_newsletter.config.settings import get_settings
from ai_newsletter.delivery import EmailSender


class NewsletterScheduler:
    """Newsletter scheduling manager."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.settings = get_settings()
        self.pipeline = None
        self.scheduler = None
        self.email_sender = None
        self.running = False
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize pipeline and scheduler components."""
        try:
            # Initialize pipeline
            self.pipeline = NewsletterPipeline(self.settings)
            print("✅ Newsletter pipeline initialized")
            
            # Initialize scheduler
            self.scheduler = DailyScheduler(config=self.settings.scheduler)
            print("✅ Daily scheduler initialized")
            
            # Initialize email sender
            self.email_sender = EmailSender(config=self.settings.email)
            print("✅ Email sender initialized")
            
        except Exception as e:
            print(f"❌ Component initialization failed: {e}")
            raise
    
    def newsletter_job_callback(self):
        """Callback function for scheduled newsletter job."""
        print(f"\n📧 Running scheduled newsletter job at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Run the pipeline
            result = self.pipeline.run_newsletter_pipeline(
                recipients=[self.settings.email.from_email],  # Send to configured email
                max_items_per_source=10,
                max_total_items=25
            )
            
            if result.success:
                print(f"✅ Newsletter sent successfully!")
                print(f"   - Items scraped: {result.items_scraped}")
                print(f"   - Newsletter generated: {result.newsletter_generated}")
                print(f"   - Email sent: {result.email_sent}")
                print(f"   - Execution time: {result.execution_time:.2f}s")
            else:
                print(f"❌ Newsletter job failed:")
                for error in result.errors:
                    print(f"   - {error}")
            
            return result.success
            
        except Exception as e:
            print(f"❌ Newsletter job error: {e}")
            return False
    
    def schedule_newsletter(self, time_str="08:00", timezone="UTC"):
        """Schedule the newsletter job."""
        print(f"⏰ Scheduling newsletter for {time_str} {timezone}")
        
        success = self.scheduler.schedule_newsletter_job(
            callback=self.newsletter_job_callback,
            job_id="daily_newsletter",
            schedule_time=time_str,
            timezone=timezone
        )
        
        if success:
            print("✅ Newsletter scheduled successfully")
            return True
        else:
            print("❌ Failed to schedule newsletter")
            return False
    
    def start_scheduler(self):
        """Start the scheduler."""
        print("🚀 Starting scheduler...")
        
        success = self.scheduler.start()
        if success:
            print("✅ Scheduler started successfully")
            self.running = True
            return True
        else:
            print("❌ Failed to start scheduler")
            return False
    
    def stop_scheduler(self):
        """Stop the scheduler."""
        print("🛑 Stopping scheduler...")
        
        success = self.scheduler.stop()
        if success:
            print("✅ Scheduler stopped successfully")
            self.running = False
            return True
        else:
            print("❌ Failed to stop scheduler")
            return False
    
    def run_test_job(self):
        """Run the newsletter job immediately for testing."""
        print("🧪 Running test newsletter job...")
        
        return self.newsletter_job_callback()
    
    def get_status(self):
        """Get scheduler status."""
        if not self.scheduler:
            return None
        
        status = self.scheduler.get_scheduler_status()
        return status
    
    def run_interactive_mode(self):
        """Run in interactive mode for testing."""
        print("\n🎮 Interactive Mode")
        print("=" * 30)
        print("Commands:")
        print("  status  - Show scheduler status")
        print("  test    - Run newsletter job now")
        print("  start   - Start scheduler")
        print("  stop    - Stop scheduler")
        print("  quit    - Exit")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "status":
                    status = self.get_status()
                    if status:
                        print(f"📊 Scheduler Status:")
                        print(f"   - Enabled: {status['enabled']}")
                        print(f"   - Running: {status['running']}")
                        print(f"   - Timezone: {status['timezone']}")
                        print(f"   - Scheduled time: {status['scheduled_time']}")
                        print(f"   - Jobs: {status['job_count']}")
                    else:
                        print("❌ Scheduler not available")
                
                elif command == "test":
                    self.run_test_job()
                
                elif command == "start":
                    self.start_scheduler()
                
                elif command == "stop":
                    self.stop_scheduler()
                
                else:
                    print("❓ Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def test_email_configuration():
    """Test email configuration."""
    print("📧 Testing Email Configuration")
    print("-" * 30)
    
    settings = get_settings()
    
    if not settings.email.from_email:
        print("❌ Email configuration incomplete")
        print("   Missing: from_email")
        return False
    
    try:
        email_sender = EmailSender(config=settings.email)
        status = email_sender.get_config_status()
        
        print(f"📊 Email Status:")
        print(f"   - Provider: {status['provider']}")
        print(f"   - Configured: {'✅' if status['configured'] else '❌'}")
        print(f"   - Connection test: {'✅' if status['connection_test'] else '❌'}")
        
        if not status['configured']:
            print(f"   - Missing config: {', '.join(status['missing_config'])}")
        
        return status['configured'] and status['connection_test']
        
    except Exception as e:
        print(f"❌ Email configuration error: {e}")
        return False


def test_pipeline_configuration():
    """Test pipeline configuration."""
    print("\n🔄 Testing Pipeline Configuration")
    print("-" * 30)
    
    settings = get_settings()
    
    try:
        pipeline = NewsletterPipeline(settings)
        status = pipeline.get_pipeline_status()
        
        print(f"📊 Pipeline Status:")
        print(f"   - Scrapers: {status['scrapers_configured']}")
        print(f"   - Generator: {'✅' if status['newsletter_generator_available'] else '❌'}")
        print(f"   - Email: {'✅' if status['email_sender_available'] else '❌'}")
        
        if status['scrapers_configured'] == 0:
            print("⚠️ No scrapers configured - newsletter will be empty")
        
        if not status['newsletter_generator_available']:
            print("⚠️ Newsletter generator not available - check OpenAI API key")
        
        if not status['email_sender_available']:
            print("⚠️ Email sender not available - check email configuration")
        
        return (status['scrapers_configured'] > 0 and 
                status['newsletter_generator_available'] and 
                status['email_sender_available'])
        
    except Exception as e:
        print(f"❌ Pipeline configuration error: {e}")
        return False


def main():
    """Main function."""
    print("🚀 CreatorPulse Scheduled Newsletter Example")
    print("=" * 60)
    
    # Test configurations
    email_ok = test_email_configuration()
    pipeline_ok = test_pipeline_configuration()
    
    if not email_ok or not pipeline_ok:
        print("\n❌ Configuration issues detected")
        print("\n💡 Required configuration:")
        print("   1. OpenAI API key (OPENAI_API_KEY)")
        print("   2. Email settings (SMTP or SendGrid)")
        print("   3. At least one content source (Reddit, RSS, YouTube)")
        print("\n📚 See config.example.json for configuration options")
        return
    
    print("\n✅ All configurations look good!")
    
    # Initialize scheduler
    try:
        scheduler_manager = NewsletterScheduler()
        
        # Schedule newsletter
        schedule_time = input("\n⏰ Enter schedule time (HH:MM) or press Enter for 08:00: ").strip()
        if not schedule_time:
            schedule_time = "08:00"
        
        timezone = input("🌍 Enter timezone or press Enter for UTC: ").strip()
        if not timezone:
            timezone = "UTC"
        
        if scheduler_manager.schedule_newsletter(schedule_time, timezone):
            # Start scheduler
            if scheduler_manager.start_scheduler():
                print(f"\n🎉 Scheduler running! Newsletter will be sent daily at {schedule_time} {timezone}")
                
                # Ask if user wants to run test
                test_now = input("\n🧪 Run test newsletter now? (y/n): ").strip().lower()
                if test_now == 'y':
                    scheduler_manager.run_test_job()
                
                # Ask if user wants interactive mode
                interactive = input("\n🎮 Enter interactive mode? (y/n): ").strip().lower()
                if interactive == 'y':
                    scheduler_manager.run_interactive_mode()
                else:
                    print("\n⏳ Scheduler is running in the background...")
                    print("   Press Ctrl+C to stop")
                    
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        print("\n👋 Stopping scheduler...")
                        scheduler_manager.stop_scheduler()
            else:
                print("❌ Failed to start scheduler")
        else:
            print("❌ Failed to schedule newsletter")
            
    except Exception as e:
        print(f"❌ Scheduler initialization failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check all API keys and credentials")
        print("   2. Verify internet connection")
        print("   3. Review error messages above")


if __name__ == "__main__":
    main()
