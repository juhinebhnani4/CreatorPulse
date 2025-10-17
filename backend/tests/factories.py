"""
Test data factories for creating realistic test data.
Uses factory_boy and faker for generating test objects.
"""

import factory
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()


class ContentItemFactory(factory.DictFactory):
    """Factory for creating content items."""

    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=8))
    url = factory.LazyAttribute(lambda _: fake.url())
    content = factory.LazyAttribute(lambda _: fake.paragraph(nb_sentences=10))
    summary = factory.LazyAttribute(lambda _: fake.paragraph(nb_sentences=3))
    source_type = factory.LazyAttribute(lambda _: random.choice(['reddit', 'rss', 'x', 'blog']))
    source_name = factory.LazyAttribute(lambda _: fake.company())
    author = factory.LazyAttribute(lambda _: fake.name())
    published_date = factory.LazyAttribute(
        lambda _: (datetime.utcnow() - timedelta(days=random.randint(0, 30))).isoformat()
    )
    relevance_score = factory.LazyAttribute(lambda _: round(random.uniform(0.5, 1.0), 2))
    sentiment_score = factory.LazyAttribute(lambda _: round(random.uniform(-1.0, 1.0), 2))


class NewsletterFactory(factory.DictFactory):
    """Factory for creating newsletters."""

    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=6))
    content_html = factory.LazyAttribute(lambda _: f"<html><body><h1>{fake.sentence()}</h1><p>{fake.paragraph()}</p></body></html>")
    content_text = factory.LazyAttribute(lambda _: fake.paragraph(nb_sentences=20))
    status = factory.LazyAttribute(lambda _: random.choice(['draft', 'pending', 'generated', 'sent']))
    generation_params = factory.LazyAttribute(lambda _: {
        "tone": "professional",
        "length": "medium",
        "include_sources": True
    })


class SubscriberFactory(factory.DictFactory):
    """Factory for creating subscribers."""

    email = factory.LazyAttribute(lambda _: fake.email())
    name = factory.LazyAttribute(lambda _: fake.name())
    status = factory.LazyAttribute(lambda _: random.choice(['active', 'unsubscribed', 'bounced']))
    metadata = factory.LazyAttribute(lambda _: {
        "signup_source": random.choice(['website', 'import', 'api']),
        "preferences": {
            "frequency": random.choice(['daily', 'weekly']),
            "topics": random.sample(['AI', 'Tech', 'Business', 'Science'], 2)
        }
    })


class SchedulerJobFactory(factory.DictFactory):
    """Factory for creating scheduler jobs."""

    name = factory.LazyAttribute(lambda _: f"{fake.word()}_job")
    cron_expression = factory.LazyAttribute(lambda _: random.choice([
        "0 9 * * *",  # Daily at 9 AM
        "0 9 * * 1",  # Weekly on Monday at 9 AM
        "0 0 1 * *",  # Monthly on 1st at midnight
    ]))
    action_type = factory.LazyAttribute(lambda _: random.choice(['scrape', 'generate', 'send']))
    action_params = factory.LazyAttribute(lambda _: {
        "workspace_id": fake.uuid4()
    })
    status = factory.LazyAttribute(lambda _: random.choice(['active', 'paused', 'completed']))


class DeliveryFactory(factory.DictFactory):
    """Factory for creating email deliveries."""

    status = factory.LazyAttribute(lambda _: random.choice(['pending', 'sending', 'delivered', 'failed']))
    recipients_count = factory.LazyAttribute(lambda _: random.randint(10, 1000))
    sent_count = factory.LazyAttribute(lambda _: random.randint(0, 1000))
    failed_count = factory.LazyAttribute(lambda _: random.randint(0, 50))
    test_mode = False


class StyleProfileFactory(factory.DictFactory):
    """Factory for creating style profiles."""

    tone = factory.LazyAttribute(lambda _: random.choice(['professional', 'casual', 'enthusiastic', 'formal']))
    vocabulary_level = factory.LazyAttribute(lambda _: random.choice(['simple', 'moderate', 'advanced']))
    avg_sentence_length = factory.LazyAttribute(lambda _: random.randint(10, 25))
    avg_paragraph_length = factory.LazyAttribute(lambda _: random.randint(3, 8))
    common_phrases = factory.LazyAttribute(lambda _: [fake.sentence(nb_words=3) for _ in range(5)])
    sample_count = factory.LazyAttribute(lambda _: random.randint(5, 50))
    confidence_score = factory.LazyAttribute(lambda _: round(random.uniform(0.6, 1.0), 2))


class TrendFactory(factory.DictFactory):
    """Factory for creating trends."""

    topic = factory.LazyAttribute(lambda _: fake.sentence(nb_words=3))
    keywords = factory.LazyAttribute(lambda _: [fake.word() for _ in range(5)])
    mention_count = factory.LazyAttribute(lambda _: random.randint(5, 100))
    sources_count = factory.LazyAttribute(lambda _: random.randint(2, 10))
    confidence_score = factory.LazyAttribute(lambda _: round(random.uniform(0.5, 1.0), 2))
    trend_type = factory.LazyAttribute(lambda _: random.choice(['emerging', 'active', 'fading']))
    explanation = factory.LazyAttribute(lambda _: fake.paragraph(nb_sentences=3))


class FeedbackFactory(factory.DictFactory):
    """Factory for creating feedback items."""

    rating = factory.LazyAttribute(lambda _: random.randint(1, 5))
    feedback_type = factory.LazyAttribute(lambda _: random.choice(['content_item', 'newsletter']))
    notes = factory.LazyAttribute(lambda _: fake.sentence(nb_words=10))
    helpful = factory.LazyAttribute(lambda _: random.choice([True, False]))


class AnalyticsEventFactory(factory.DictFactory):
    """Factory for creating analytics events."""

    event_type = factory.LazyAttribute(lambda _: random.choice(['open', 'click', 'bounce', 'spam_report', 'unsubscribe']))
    timestamp = factory.LazyAttribute(lambda _: datetime.utcnow().isoformat())
    user_agent = factory.LazyAttribute(lambda _: fake.user_agent())
    ip_address = factory.LazyAttribute(lambda _: fake.ipv4())
    metadata = factory.LazyAttribute(lambda _: {
        "device": random.choice(['desktop', 'mobile', 'tablet']),
        "os": random.choice(['Windows', 'macOS', 'Linux', 'iOS', 'Android'])
    })


# Helper functions for batch creation

def create_content_items(count=10, **kwargs):
    """Create multiple content items."""
    return [ContentItemFactory(**kwargs) for _ in range(count)]


def create_subscribers(count=10, **kwargs):
    """Create multiple subscribers."""
    return [SubscriberFactory(**kwargs) for _ in range(count)]


def create_newsletters(count=5, **kwargs):
    """Create multiple newsletters."""
    return [NewsletterFactory(**kwargs) for _ in range(count)]


def create_trends(count=5, **kwargs):
    """Create multiple trends."""
    return [TrendFactory(**kwargs) for _ in range(count)]


def create_analytics_events(count=100, **kwargs):
    """Create multiple analytics events."""
    return [AnalyticsEventFactory(**kwargs) for _ in range(count)]
