"""
Minimal Streamlit app to test the core functionality.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st
import pandas as pd
from datetime import datetime

from ai_newsletter.scrapers import RedditScraper
from ai_newsletter.models.content import ContentItem

st.title("🧪 Minimal Test App")

# Session state
if 'items' not in st.session_state:
    st.session_state.items = []

st.write(f"Session state items type: {type(st.session_state.items)}")
st.write(f"Session state items length: {len(st.session_state.items)}")

# Fetch button
if st.button("Fetch Data"):
    with st.spinner("Fetching..."):
        scraper = RedditScraper()
        fetched_items = scraper.fetch_content(subreddit='AI_Agents', limit=5)
        st.session_state.items = fetched_items
        st.success(f"Fetched {len(fetched_items)} items")

# Get items
items = st.session_state.items

st.write(f"Items variable type: {type(items)}")
st.write(f"Items variable length: {len(items)}")

if not items:
    st.warning("No items. Click 'Fetch Data' button.")
    st.stop()

st.write(f"First item type: {type(items[0])}")
st.write(f"First item has to_dict: {hasattr(items[0], 'to_dict')}")

# Try conversion
try:
    st.write("Attempting list comprehension...")
    df_data = [item.to_dict() for item in items]
    st.success(f"✅ Successfully converted {len(df_data)} items")
    
    df = pd.DataFrame(df_data)
    st.write(f"DataFrame shape: {df.shape}")
    
    st.dataframe(df[['title', 'source', 'score', 'comments_count']])
    
except Exception as e:
    st.error(f"❌ Error: {e}")
    st.error(f"Error type: {type(e)}")
    import traceback
    st.code(traceback.format_exc())

