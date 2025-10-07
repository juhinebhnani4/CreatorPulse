"""
Streamlit application for AI Newsletter Scraper.
Supports multiple content sources (Reddit, RSS, Blogs, X).
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List

from ai_newsletter.scrapers import RedditScraper, RSSFeedScraper, BlogScraper
from ai_newsletter.scrapers.x_scraper import XScraper
from ai_newsletter.models.content import ContentItem
from ai_newsletter.config import get_settings
from ai_newsletter.utils import ScraperRegistry


def main():
    """Main Streamlit application."""
    
    # Page configuration
    st.set_page_config(
        page_title="AI Newsletter Scraper",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Title and description
    st.title("🤖 AI Newsletter Content Scraper")
    st.markdown("""
    Aggregate AI-related content from multiple sources including Reddit, RSS feeds, blogs, and X (Twitter).
    Filter, sort, and explore the latest discussions and articles about artificial intelligence.
    """)
    
    # Load settings
    settings = get_settings()
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Source selection
    st.sidebar.subheader("📡 Sources")
    
    sources = {
        "Reddit": st.sidebar.checkbox("Reddit", value=True),
        "RSS Feeds": st.sidebar.checkbox("RSS Feeds", value=False),
        "Blogs": st.sidebar.checkbox("Blogs", value=False),
        "X (Twitter)": st.sidebar.checkbox("X (Twitter)", value=False),
    }
    
    # Source-specific settings
    reddit_params = {}
    rss_params = {}
    blog_params = {}
    x_params = {}
    
    if sources["Reddit"]:
        with st.sidebar.expander("Reddit Settings"):
            subreddits_input = st.text_input(
                "Subreddits (comma-separated)",
                value="AI_Agents,MachineLearning"
            )
            reddit_params['subreddits'] = [s.strip() for s in subreddits_input.split(',')]
            reddit_params['sort'] = st.selectbox("Sort", ["hot", "new", "top", "rising"])
            reddit_params['limit'] = st.slider("Posts per subreddit", 5, 50, 10)
    
    if sources["RSS Feeds"]:
        with st.sidebar.expander("RSS Settings"):
            default_feeds = [
                "https://blog.openai.com/rss/",
                "https://ai.googleblog.com/feeds/posts/default"
            ]
            feeds_input = st.text_area(
                "Feed URLs (one per line)",
                value="\n".join(default_feeds)
            )
            rss_params['feed_urls'] = [f.strip() for f in feeds_input.split('\n') if f.strip()]
            rss_params['limit'] = st.slider("Entries per feed", 5, 50, 10, key="rss_limit")
    
    if sources["Blogs"]:
        with st.sidebar.expander("Blog Settings"):
            blog_urls = st.text_area(
                "Blog URLs (one per line)",
                value=""
            )
            blog_params['urls'] = [u.strip() for u in blog_urls.split('\n') if u.strip()]
            blog_params['template'] = st.selectbox(
                "Blog Platform",
                ["wordpress", "medium", "ghost", "substack"]
            )
            blog_params['limit'] = st.slider("Articles per blog", 5, 20, 10, key="blog_limit")
    
    if sources["X (Twitter)"]:
        with st.sidebar.expander("X (Twitter) Settings"):
            st.warning("⚠️ Requires API credentials (see config)")
            x_query = st.text_input("Search query or hashtag", value="#AI")
            x_params['query'] = x_query
            x_params['limit'] = st.slider("Posts", 5, 50, 10, key="x_limit")
    
    # General settings
    st.sidebar.subheader("🔧 General")
    max_total_items = st.sidebar.number_input("Max total items", 10, 500, 100)
    
    # Fetch button
    fetch_button = st.sidebar.button("🔄 Fetch Content", type="primary", use_container_width=True)
    
    # Session state for caching results
    if 'content_items' not in st.session_state:
        st.session_state.content_items = []
    if 'last_fetch' not in st.session_state:
        st.session_state.last_fetch = None
    
    # Fetch content
    if fetch_button or len(st.session_state.content_items) == 0:
        all_items = []
        
        with st.spinner("Fetching content from selected sources..."):
            # Reddit
            if sources["Reddit"]:
                with st.spinner("📱 Fetching from Reddit..."):
                    try:
                        reddit_scraper = RedditScraper()
                        for subreddit in reddit_params.get('subreddits', ['AI_Agents']):
                            fetched_items = reddit_scraper.fetch_content(
                                subreddit=subreddit,
                                limit=reddit_params.get('limit', 10),
                                sort=reddit_params.get('sort', 'hot')
                            )
                            all_items.extend(fetched_items)
                            st.sidebar.success(f"✓ r/{subreddit}: {len(fetched_items)} posts")
                    except Exception as e:
                        st.sidebar.error(f"❌ Reddit error: {e}")
            
            # RSS
            if sources["RSS Feeds"]:
                with st.spinner("📰 Fetching from RSS feeds..."):
                    try:
                        rss_scraper = RSSFeedScraper()
                        fetched_items = rss_scraper.fetch_content(
                            feed_urls=rss_params.get('feed_urls', []),
                            limit=rss_params.get('limit', 10)
                        )
                        all_items.extend(fetched_items)
                        st.sidebar.success(f"✓ RSS: {len(fetched_items)} articles")
                    except Exception as e:
                        st.sidebar.error(f"❌ RSS error: {e}")
            
            # Blogs
            if sources["Blogs"] and blog_params.get('urls'):
                with st.spinner("📝 Fetching from blogs..."):
                    try:
                        blog_scraper = BlogScraper()
                        for url in blog_params.get('urls', []):
                            fetched_items = blog_scraper.fetch_with_template(
                                url=url,
                                template_name=blog_params.get('template', 'wordpress'),
                                limit=blog_params.get('limit', 10)
                            )
                            all_items.extend(fetched_items)
                            st.sidebar.success(f"✓ {url}: {len(fetched_items)} articles")
                    except Exception as e:
                        st.sidebar.error(f"❌ Blog error: {e}")
            
            # X (Twitter)
            if sources["X (Twitter)"]:
                with st.spinner("🐦 Fetching from X..."):
                    try:
                        x_scraper = XScraper(
                            api_key=settings.x.api_key,
                            api_secret=settings.x.api_secret,
                            access_token=settings.x.access_token,
                            access_token_secret=settings.x.access_token_secret,
                            bearer_token=settings.x.bearer_token
                        )
                        fetched_items = x_scraper.fetch_content(
                            query=x_params.get('query', '#AI'),
                            limit=x_params.get('limit', 10)
                        )
                        all_items.extend(fetched_items)
                        st.sidebar.success(f"✓ X: {len(fetched_items)} posts")
                    except Exception as e:
                        st.sidebar.error(f"❌ X error: {e}")
        
        # Limit total items
        st.session_state.content_items = all_items[:max_total_items]
        st.session_state.last_fetch = datetime.now()
    
    # Get items from session state
    items = st.session_state.content_items
    
    # Debug: Check what we got
    if not isinstance(items, list):
        st.error(f"❌ Debug: items is {type(items)}, not a list!")
        st.stop()
    
    if len(items) == 0:
        st.warning("⚠️ No content fetched. Please select at least one source and click 'Fetch Content'.")
        st.stop()
    
    # Convert to DataFrame
    try:
        df_data = [item.to_dict() for item in items]
    except TypeError as e:
        st.error(f"❌ Error converting items to dict: {e}")
        st.error(f"Items type: {type(items)}")
        st.error(f"First item type: {type(items[0]) if items else 'N/A'}")
        st.stop()
    df = pd.DataFrame(df_data)
    
    # Format datetime columns
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['created_date'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
    
    # Summary statistics
    st.subheader("📊 Summary")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Items", len(df))
    
    with col2:
        unique_sources = df['source'].nunique()
        st.metric("Sources", unique_sources)
    
    with col3:
        avg_score = df['score'].mean()
        st.metric("Avg Score", f"{avg_score:.1f}")
    
    with col4:
        total_comments = df['comments_count'].sum()
        st.metric("Total Comments", int(total_comments))
    
    with col5:
        if st.session_state.last_fetch:
            last_fetch = st.session_state.last_fetch.strftime('%H:%M:%S')
            st.metric("Last Fetch", last_fetch)
    
    # Source distribution
    st.subheader("📈 Distribution by Source")
    source_counts = df['source'].value_counts()
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.bar_chart(source_counts)
    
    with col2:
        st.dataframe(source_counts.reset_index().rename(columns={'index': 'Source', 'source': 'Count'}))
    
    st.divider()
    
    # Filters
    st.subheader("🔍 Filters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        source_filter = st.multiselect(
            "Source",
            options=df['source'].unique().tolist(),
            default=df['source'].unique().tolist()
        )
    
    with col2:
        min_score = st.number_input("Min Score", min_value=0, value=0)
    
    with col3:
        min_comments = st.number_input("Min Comments", min_value=0, value=0)
    
    with col4:
        # Date filter
        days_back = st.selectbox("Time Period", [1, 7, 30, 90, 365, "All"])
        
    # Apply filters
    df_filtered = df[df['source'].isin(source_filter)]
    df_filtered = df_filtered[df_filtered['score'] >= min_score]
    df_filtered = df_filtered[df_filtered['comments_count'] >= min_comments]
    
    if days_back != "All":
        cutoff_date = datetime.now() - timedelta(days=days_back)
        df_filtered = df_filtered[df_filtered['created_at'] >= cutoff_date]
    
    st.info(f"📋 Showing {len(df_filtered)} items (filtered from {len(df)} total)")
    
    # Sort options
    st.subheader("📊 Sort")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sort_by = st.selectbox(
            "Sort by",
            ['score', 'comments_count', 'created_at', 'title', 'author'],
            index=0
        )
    
    with col2:
        sort_order = st.selectbox("Order", ['Descending', 'Ascending'])
    
    # Apply sorting
    ascending = sort_order == 'Ascending'
    df_sorted = df_filtered.sort_values(by=sort_by, ascending=ascending)
    
    # Display options
    st.subheader("📋 Content")
    
    display_columns = st.multiselect(
        "Select columns to display",
        options=['title', 'source', 'author', 'score', 'comments_count', 'created_date', 'category', 'tags', 'summary'],
        default=['title', 'source', 'author', 'score', 'comments_count', 'created_date']
    )
    
    if display_columns:
        # Display table
        st.dataframe(
            df_sorted[display_columns],
            use_container_width=True,
            height=500
        )
        
        # Download button
        csv = df_sorted.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"ai_newsletter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Detailed view
    st.divider()
    st.subheader("🔍 Detailed View")
    
    if len(df_sorted) > 0:
        # Select item
        item_titles = df_sorted['title'].tolist()
        selected_idx = st.selectbox(
            "Select an item to view details",
            range(len(item_titles)),
            format_func=lambda x: f"{item_titles[x][:80]}..."
        )
        
        selected_item = df_sorted.iloc[selected_idx]
        
        # Display details
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {selected_item['title']}")
            
            if selected_item.get('summary'):
                st.markdown("**Summary:**")
                st.write(selected_item['summary'])
            
            if selected_item.get('content') and selected_item['content'] != selected_item.get('summary'):
                with st.expander("View full content"):
                    st.write(selected_item['content'])
        
        with col2:
            st.markdown("**Metadata**")
            st.markdown(f"**Source:** {selected_item['source']}")
            if selected_item.get('author'):
                st.markdown(f"**Author:** {selected_item['author']}")
            st.markdown(f"**Score:** {selected_item['score']}")
            st.markdown(f"**Comments:** {selected_item['comments_count']}")
            st.markdown(f"**Date:** {selected_item['created_date']}")
            
            if selected_item.get('category'):
                st.markdown(f"**Category:** {selected_item['category']}")
            
            if selected_item.get('tags') and selected_item['tags']:
                tags_str = ', '.join(selected_item['tags']) if isinstance(selected_item['tags'], list) else selected_item['tags']
                st.markdown(f"**Tags:** {tags_str}")
            
            st.markdown("**Links:**")
            if selected_item.get('source_url'):
                st.markdown(f"[🔗 View Original]({selected_item['source_url']})")
            if selected_item.get('external_url') and selected_item['external_url'] != selected_item.get('source_url'):
                st.markdown(f"[🌐 External Link]({selected_item['external_url']})")
    
    # Footer
    st.divider()
    st.markdown(f"""
    ---
    **AI Newsletter Scraper** | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
    Aggregating content from multiple sources to keep you informed about AI developments.
    """)


if __name__ == "__main__":
    main()

