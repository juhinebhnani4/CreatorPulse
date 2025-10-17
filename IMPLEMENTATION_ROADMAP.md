# CreatorPulse - Implementation Roadmap

**Last Updated:** January 2025
**Status:** In Development
**Target:** Match product vision from [create.md](create.md)

---

## 📋 Executive Summary

### Current State Analysis

#### ✅ What's Working Well (60% Complete)
- **Source Connections:** Reddit, RSS, Blogs, X/Twitter, YouTube scrapers ✅
- **Content Aggregation:** Multi-source scraping with intelligent filtering ✅
- **Newsletter Generation:** AI-powered drafts with OpenAI/OpenRouter ✅
- **Email Delivery:** SMTP + SendGrid integration ✅
- **Scheduling:** Daily scheduler with pipeline automation ✅
- **Web Dashboard:** Streamlit UI for source management ✅

#### ❌ Critical Gaps (40% Missing)
- **Writing Style Trainer:** No voice matching capability 🔴
- **Trends Detection:** No emerging topic identification 🔴
- **Multi-Client Support:** Single-tenant only 🔴
- **Feedback Loop:** No learning from user edits 🟡
- **Engagement Analytics:** No open/CTR tracking 🟡
- **Agency Features:** No workspace isolation 🔴

### Vision vs Reality

| Vision (create.md) | Current Reality | Gap |
|-------------------|-----------------|-----|
| "70%+ ready-to-send draft in <20 minutes" | Generic AI drafts require heavy editing | 🔴 **CRITICAL** |
| "Matches your unique writing style" | Only generic tones (professional/casual) | 🔴 **CRITICAL** |
| "Surfaces emerging trends automatically" | Just shows high-engagement content | 🔴 **CRITICAL** |
| "Learns from your feedback over time" | No feedback mechanism | 🟡 Medium |
| "Scalable for agencies (multiple clients)" | Single config.json file | 🔴 **CRITICAL** |
| "Proves ROI with engagement metrics" | No analytics tracking | 🟡 Medium |

### Priority Roadmap

**Sprint 1 (Week 1):** Foundation - Multi-Client Workspace System
**Sprint 2 (Week 2):** Core Differentiators - Style Trainer + Trends Engine
**Sprint 3 (Week 3):** Learning & Analytics - Feedback Loop + Engagement Tracking
**Sprint 4 (Week 4):** Polish - UI/UX improvements + Documentation

---

## 🎯 Feature Breakdown

---

## Feature 1: Writing Style Trainer

**Priority:** P0 - CRITICAL 🔴
**Effort:** 2-3 days
**Sprint:** Sprint 2

### User Story
> "As a newsletter creator, I want the AI to write in MY unique voice so that I don't spend 90 minutes editing every draft to sound like me."

### Problem Statement
- Current AI generates generic content in basic tones (professional, casual, technical)
- Users must heavily edit to match their personal writing style
- No way to train the AI on past successful newsletters
- Draft acceptance rate is low (<40% vs target 70%)

### Success Criteria
- [ ] User can upload 20+ past newsletter samples
- [ ] System analyzes and extracts writing style patterns
- [ ] Generated newsletters match user's voice (verified by comparison)
- [ ] Draft acceptance rate improves to >70%
- [ ] Editing time reduced from 90 minutes to <20 minutes

### Technical Implementation

#### 1. Style Profile Data Structure
```python
@dataclass
class StyleProfile:
    """Represents a user's unique writing style"""

    # Voice characteristics
    tone: str  # "conversational", "authoritative", "humorous"
    formality_level: float  # 0.0 (casual) to 1.0 (formal)

    # Sentence patterns
    avg_sentence_length: float
    sentence_length_variety: float  # std deviation
    question_frequency: float  # questions per 100 words

    # Vocabulary preferences
    vocabulary_level: str  # "simple", "intermediate", "advanced"
    favorite_phrases: List[str]  # frequently used expressions
    avoided_words: List[str]  # words user never uses

    # Structural preferences
    typical_intro_style: str  # "question", "statement", "anecdote"
    section_count: int  # average sections per newsletter
    uses_emojis: bool
    emoji_frequency: float

    # Example sentences
    example_intros: List[str]
    example_transitions: List[str]
    example_conclusions: List[str]

    # Metadata
    trained_on_count: int  # number of sample newsletters
    last_updated: datetime
```

#### 2. New Module: `src/ai_newsletter/generators/style_trainer.py`

**Core Functions:**
```python
class StyleTrainer:
    def analyze_samples(self, sample_texts: List[str]) -> StyleProfile:
        """
        Analyze sample newsletters to extract writing style patterns.

        Steps:
        1. Sentence analysis (length, structure, complexity)
        2. Vocabulary analysis (word frequency, sophistication)
        3. Tone detection (sentiment, formality)
        4. Structural analysis (intro/body/conclusion patterns)
        5. Extract characteristic examples
        """

    def create_style_prompt(self, style_profile: StyleProfile) -> str:
        """
        Generate a system prompt that instructs AI to write in user's style.

        Uses few-shot learning with extracted examples.
        """

    def validate_style_match(self,
                            generated_text: str,
                            style_profile: StyleProfile) -> float:
        """
        Score how well generated text matches the style profile.
        Returns similarity score 0.0 to 1.0.
        """
```

**Text Analysis Methods:**
```python
def _analyze_sentences(self, text: str) -> Dict:
    """Extract sentence-level patterns"""
    # Use NLTK or spaCy for:
    - Average sentence length
    - Sentence variety (std dev)
    - Question frequency
    - Exclamation usage
    - Complex vs simple sentences

def _analyze_vocabulary(self, text: str) -> Dict:
    """Extract vocabulary patterns"""
    # Analyze:
    - Word frequency distribution
    - Lexical diversity (unique words / total words)
    - Reading level (Flesch-Kincaid)
    - Common phrases (n-grams)
    - Avoided words

def _analyze_tone(self, text: str) -> Dict:
    """Detect tone and formality"""
    # Use:
    - Sentiment analysis (positive/negative/neutral)
    - Formality detection (contractions, colloquialisms)
    - Humor markers (puns, jokes, sarcasm)
    - Authority markers (citations, statistics)

def _analyze_structure(self, text: str) -> Dict:
    """Extract structural patterns"""
    # Identify:
    - Section count and headings
    - Intro style (question/statement/story)
    - Transition words usage
    - Conclusion patterns
    - Emoji usage patterns
```

#### 3. Integration with NewsletterGenerator

**Modify:** `src/ai_newsletter/generators/newsletter_generator.py`

```python
class NewsletterGenerator:
    def __init__(self, config, style_profile: Optional[StyleProfile] = None):
        self.config = config
        self.style_profile = style_profile  # NEW

    def _build_prompt(self, items, title, intro, footer):
        # MODIFIED: Include style instructions if profile exists
        if self.style_profile:
            style_instructions = self._create_style_instructions()
            prompt = f"{style_instructions}\n\n{prompt}"
        return prompt

    def _create_style_instructions(self) -> str:
        """Generate style-specific prompt instructions"""
        profile = self.style_profile

        instructions = f"""
        Write in this specific style:
        - Tone: {profile.tone} ({profile.formality_level:.0%} formal)
        - Average sentence length: {profile.avg_sentence_length} words
        - Use these characteristic phrases: {', '.join(profile.favorite_phrases[:5])}
        - Avoid these words: {', '.join(profile.avoided_words[:10])}
        - Intro style: {profile.typical_intro_style}
        - Emoji usage: {'Include emojis' if profile.uses_emojis else 'No emojis'}

        Example of your writing style:
        Intro: "{profile.example_intros[0]}"
        Transition: "{profile.example_transitions[0]}"
        """
        return instructions
```

#### 4. Storage

**New file:** `workspaces/{workspace}/style_profile.json`

```json
{
  "tone": "conversational",
  "formality_level": 0.35,
  "avg_sentence_length": 15.8,
  "sentence_length_variety": 6.2,
  "question_frequency": 0.12,
  "vocabulary_level": "intermediate",
  "favorite_phrases": [
    "Here's the thing",
    "Let's dive in",
    "Quick thought"
  ],
  "avoided_words": ["synergy", "leverage", "utilize"],
  "typical_intro_style": "question",
  "section_count": 4,
  "uses_emojis": true,
  "emoji_frequency": 0.08,
  "example_intros": ["Ever wonder why AI agents are everywhere now?"],
  "example_transitions": ["Now here's where it gets interesting:"],
  "example_conclusions": ["That's all for today. Stay curious!"],
  "trained_on_count": 23,
  "last_updated": "2025-01-20T10:30:00Z"
}
```

### UI Changes

**Location:** Settings Tab → New Section: "📝 Writing Style Training"

**UI Elements:**
```python
with st.expander("📝 Writing Style Training", expanded=False):
    st.markdown("""
    Upload 20+ past newsletters to train the AI to write in YOUR unique voice.
    The more samples you provide, the better the match!
    """)

    # Input method 1: Paste text
    sample_text = st.text_area(
        "Paste newsletter samples (separate with '---')",
        height=300,
        help="Paste at least 20 past newsletters, separated by '---'"
    )

    # Input method 2: Upload CSV/TXT
    uploaded_file = st.file_uploader(
        "Or upload a file",
        type=['txt', 'csv', 'json'],
        help="One newsletter per line or in separate rows"
    )

    # Train button
    if st.button("🎓 Train Style Model", type="primary"):
        with st.spinner("Analyzing your writing style..."):
            # Parse samples
            samples = parse_samples(sample_text or uploaded_file)

            if len(samples) < 10:
                st.warning("⚠️ Need at least 10 samples for accurate training. Please add more.")
                return

            # Train style model
            trainer = StyleTrainer()
            style_profile = trainer.analyze_samples(samples)

            # Save to workspace
            save_style_profile(current_workspace, style_profile)

            st.success(f"✅ Style trained on {len(samples)} samples!")

            # Show style summary
            st.subheader("Your Writing Style Profile")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tone", style_profile.tone.title())
                st.metric("Formality", f"{style_profile.formality_level:.0%}")
            with col2:
                st.metric("Avg Sentence Length", f"{style_profile.avg_sentence_length:.1f} words")
                st.metric("Emoji Usage", "Yes" if style_profile.uses_emojis else "No")
            with col3:
                st.metric("Question Frequency", f"{style_profile.question_frequency:.0%}")
                st.metric("Samples Analyzed", style_profile.trained_on_count)

    # Show current style profile if exists
    current_profile = load_style_profile(current_workspace)
    if current_profile:
        st.info(f"✅ Style profile active (trained on {current_profile.trained_on_count} samples)")
        if st.button("🔄 Retrain Style"):
            delete_style_profile(current_workspace)
            st.rerun()
```

### Testing Checklist
- [ ] Can parse 20+ newsletter samples from text input
- [ ] Can parse newsletters from uploaded CSV/TXT files
- [ ] Style analysis completes in <30 seconds
- [ ] Generated style profile is accurate (manual verification)
- [ ] Newsletter generator uses style profile when available
- [ ] Generated newsletters match writing style (comparison test)
- [ ] Style profile persists across sessions
- [ ] Can retrain style with new samples
- [ ] Works with different writing styles (formal, casual, technical, humorous)
- [ ] Error handling for insufficient samples

### Files to Create/Modify

**New Files:**
- `src/ai_newsletter/generators/style_trainer.py` (~400 lines)
- `src/ai_newsletter/models/style_profile.py` (~100 lines)
- `tests/unit/test_style_trainer.py` (~200 lines)

**Modified Files:**
- `src/ai_newsletter/generators/newsletter_generator.py` (~50 line changes)
- `src/streamlit_app.py` - settings_tab() (~100 lines added)

### Dependencies
- `nltk` or `spacy` for NLP analysis
- `textstat` for readability metrics
- `scikit-learn` for text analysis (optional)

### Estimated Effort
- **Analysis Algorithm:** 8 hours
- **Integration with Generator:** 4 hours
- **UI Implementation:** 4 hours
- **Testing:** 4 hours
- **Total:** 20 hours (~2.5 days)

---

## Feature 2: Trends Detection Engine

**Priority:** P0 - CRITICAL 🔴
**Effort:** 3-4 days
**Sprint:** Sprint 2

### User Story
> "As a newsletter creator, I want to automatically discover emerging trends in my niche so I can write about hot topics before they go mainstream."

### Problem Statement
- Current system just shows high-engagement content
- No detection of emerging topics or spike patterns
- Users must manually identify trends by reading everything
- Missing the "insights curator" value proposition
- No "Trends to Watch" section in newsletters

### Success Criteria
- [ ] Automatically detect 3-5 emerging trends from aggregated content
- [ ] Show trend strength/confidence score
- [ ] Identify cross-source trends (validated across multiple sources)
- [ ] Detect velocity spikes (topics gaining momentum)
- [ ] Include "🔥 Trends to Watch" section in newsletter
- [ ] Explain WHY each trend is important

### Technical Implementation

#### 1. Trend Data Structure
```python
@dataclass
class Trend:
    """Represents an emerging trend detected from content"""

    # Core attributes
    topic: str  # "AI Agents", "Open Source LLMs", etc.
    keywords: List[str]  # ["ai", "agents", "automation"]

    # Strength indicators
    strength_score: float  # 0.0 to 1.0 (confidence level)
    mention_count: int  # total mentions
    velocity: float  # mentions per hour (spike indicator)

    # Sources
    sources: List[str]  # ["reddit", "youtube", "rss"]
    source_count: int  # number of different sources

    # Evidence
    key_items: List[ContentItem]  # top 3-5 items about this trend
    first_seen: datetime
    peak_time: datetime

    # Context
    explanation: str  # AI-generated explanation of why it's trending
    related_topics: List[str]

    # Metadata
    detected_at: datetime
    confidence_level: str  # "high", "medium", "low"
```

#### 2. New Module: `src/ai_newsletter/analysis/trend_detector.py`

**Core Class:**
```python
class TrendDetector:
    def __init__(self, min_confidence: float = 0.6):
        self.min_confidence = min_confidence
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 3)
        )

    def detect_trends(self,
                     current_items: List[ContentItem],
                     historical_items: Optional[List[ContentItem]] = None,
                     max_trends: int = 5) -> List[Trend]:
        """
        Detect emerging trends from content items.

        Multi-stage detection:
        1. Topic clustering (find what people are talking about)
        2. Velocity detection (find what's NEWLY popular)
        3. Cross-source validation (ignore single-source noise)
        4. Anomaly detection (find unusual spikes)
        5. AI explanation generation (explain the trend)
        """

        # Stage 1: Extract topics
        topics = self._extract_topics(current_items)

        # Stage 2: Calculate velocity (if historical data available)
        if historical_items:
            topics_with_velocity = self._calculate_velocity(
                topics, current_items, historical_items
            )
        else:
            topics_with_velocity = topics

        # Stage 3: Cross-source validation
        validated_topics = self._validate_cross_source(topics_with_velocity)

        # Stage 4: Score and rank
        scored_trends = self._score_trends(validated_topics)

        # Stage 5: Generate explanations
        trends = self._generate_explanations(scored_trends)

        # Return top N trends above confidence threshold
        return [t for t in trends if t.strength_score >= self.min_confidence][:max_trends]
```

**Detection Methods:**

```python
def _extract_topics(self, items: List[ContentItem]) -> List[Dict]:
    """
    Extract topics using TF-IDF + clustering.
    """
    # Combine title + summary + content
    texts = [f"{item.title} {item.summary or ''}" for item in items]

    # TF-IDF vectorization
    tfidf_matrix = self.vectorizer.fit_transform(texts)

    # K-means clustering (5-10 clusters)
    n_clusters = min(10, len(items) // 5)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(tfidf_matrix)

    # Extract topic keywords for each cluster
    topics = []
    for cluster_id in range(n_clusters):
        cluster_items = [items[i] for i in range(len(items)) if clusters[i] == cluster_id]
        keywords = self._extract_keywords(cluster_items)

        topics.append({
            'topic': keywords[0],  # main keyword
            'keywords': keywords,
            'items': cluster_items,
            'cluster_id': cluster_id
        })

    return topics

def _calculate_velocity(self,
                        topics: List[Dict],
                        current_items: List[ContentItem],
                        historical_items: List[ContentItem]) -> List[Dict]:
    """
    Calculate mention velocity (spike detection).
    """
    for topic in topics:
        keywords = topic['keywords']

        # Count mentions in current window (last 24h)
        current_mentions = sum(
            1 for item in current_items
            if any(kw.lower() in item.title.lower() for kw in keywords)
        )

        # Count mentions in historical window (previous 24h)
        historical_mentions = sum(
            1 for item in historical_items
            if any(kw.lower() in item.title.lower() for kw in keywords)
        )

        # Calculate velocity (percentage increase)
        if historical_mentions > 0:
            velocity = (current_mentions - historical_mentions) / historical_mentions
        else:
            velocity = current_mentions  # new topic

        topic['mention_count'] = current_mentions
        topic['velocity'] = velocity

    return topics

def _validate_cross_source(self, topics: List[Dict]) -> List[Dict]:
    """
    Filter topics that appear in multiple sources (reduce noise).
    """
    validated = []

    for topic in topics:
        sources = set(item.source for item in topic['items'])

        # Require at least 2 different sources for validation
        if len(sources) >= 2:
            topic['sources'] = list(sources)
            topic['source_count'] = len(sources)
            validated.append(topic)

    return validated

def _score_trends(self, topics: List[Dict]) -> List[Dict]:
    """
    Score trends based on multiple factors.
    """
    for topic in topics:
        score = 0.0

        # Factor 1: Mention count (30% weight)
        mention_score = min(topic['mention_count'] / 20, 1.0)
        score += mention_score * 0.3

        # Factor 2: Velocity (40% weight)
        velocity_score = min(topic.get('velocity', 0) / 2.0, 1.0)
        score += velocity_score * 0.4

        # Factor 3: Source diversity (30% weight)
        source_score = min(topic['source_count'] / 4, 1.0)
        score += source_score * 0.3

        topic['strength_score'] = score

        # Confidence level
        if score >= 0.75:
            topic['confidence_level'] = 'high'
        elif score >= 0.5:
            topic['confidence_level'] = 'medium'
        else:
            topic['confidence_level'] = 'low'

    # Sort by score
    topics.sort(key=lambda x: x['strength_score'], reverse=True)

    return topics

def _generate_explanations(self, topics: List[Dict]) -> List[Trend]:
    """
    Use AI to generate human-readable trend explanations.
    """
    trends = []

    for topic_data in topics:
        # Create prompt for AI explanation
        items_summary = "\n".join([
            f"- {item.title} ({item.source})"
            for item in topic_data['items'][:5]
        ])

        prompt = f"""
        This topic is trending: {topic_data['topic']}
        Related content:
        {items_summary}

        Explain in 1-2 sentences why this is trending and why it matters.
        Be concise and insightful.
        """

        # Call AI (reuse OpenAI/OpenRouter client)
        explanation = self._call_ai_for_explanation(prompt)

        # Create Trend object
        trend = Trend(
            topic=topic_data['topic'],
            keywords=topic_data['keywords'],
            strength_score=topic_data['strength_score'],
            mention_count=topic_data['mention_count'],
            velocity=topic_data.get('velocity', 0),
            sources=topic_data['sources'],
            source_count=topic_data['source_count'],
            key_items=topic_data['items'][:3],
            first_seen=min(item.created_at for item in topic_data['items']),
            peak_time=datetime.now(),
            explanation=explanation,
            related_topics=[],
            detected_at=datetime.now(),
            confidence_level=topic_data['confidence_level']
        )

        trends.append(trend)

    return trends

def _extract_keywords(self, items: List[ContentItem]) -> List[str]:
    """Extract top keywords from a cluster of items."""
    # Combine all text
    text = " ".join([f"{item.title} {item.summary or ''}" for item in items])

    # Use TF-IDF to find important words
    # (simplified - could use RAKE, TextRank, etc.)
    words = text.lower().split()
    word_freq = Counter(words)

    # Filter stopwords and get top keywords
    stopwords = set(['the', 'a', 'an', 'in', 'on', 'at', 'to', 'for'])
    keywords = [
        word for word, freq in word_freq.most_common(10)
        if word not in stopwords and len(word) > 3
    ]

    return keywords[:5]
```

#### 3. Historical Data Storage

**New file:** `workspaces/{workspace}/historical_content.json`

Store last 7 days of content for velocity calculations:
```json
{
  "2025-01-20": [
    {"title": "...", "source": "reddit", "created_at": "..."},
    ...
  ],
  "2025-01-19": [...],
  ...
}
```

**Utility functions:**
```python
def save_historical_content(workspace: str, items: List[ContentItem]):
    """Append today's content to historical data"""

def load_historical_content(workspace: str, days: int = 7) -> List[ContentItem]:
    """Load content from last N days"""

def cleanup_old_historical_data(workspace: str, keep_days: int = 7):
    """Delete historical data older than N days"""
```

#### 4. Integration with NewsletterGenerator

**Modify:** `src/ai_newsletter/generators/newsletter_generator.py`

```python
class NewsletterGenerator:
    def generate_newsletter(self, content_items, ...):
        # EXISTING: Select diverse content
        items = self._select_diverse_content(content_items, max_items)

        # NEW: Detect trends
        trend_detector = TrendDetector()
        historical_items = load_historical_content(workspace)
        trends = trend_detector.detect_trends(content_items, historical_items)

        # NEW: Add trends to newsletter
        if trends:
            trends_html = self._format_trends_section(trends)
            # Insert at top of newsletter

        # Continue with normal newsletter generation
        ...
```

**New HTML template section:**
```html
<div class="trends-section">
    <h2>🔥 Trends to Watch</h2>
    <p>Emerging topics detected across your sources:</p>

    {{for trend in trends}}
    <div class="trend-item">
        <h3>
            <span class="trend-strength">{{trend.strength_emoji}}</span>
            {{trend.topic}}
        </h3>
        <div class="trend-meta">
            <span>{{trend.source_count}} sources</span>
            <span>{{trend.mention_count}} mentions</span>
            <span class="trend-velocity">
                {{if trend.velocity > 1}}↗️ +{{trend.velocity}}%{{endif}}
            </span>
        </div>
        <p class="trend-explanation">{{trend.explanation}}</p>
        <div class="trend-links">
            {{for item in trend.key_items[:3]}}
            <a href="{{item.source_url}}">📄 {{item.title}}</a>
            {{endfor}}
        </div>
    </div>
    {{endfor}}
</div>
```

### UI Changes

**Location:** Content Scraper Tab → Add "🔥 Trends" Section

```python
# After showing content table
if len(items) > 10:  # Need enough data for trend detection
    st.subheader("🔥 Detected Trends")

    with st.spinner("Analyzing trends..."):
        trend_detector = TrendDetector()
        historical_items = load_historical_content(workspace, days=7)
        trends = trend_detector.detect_trends(items, historical_items)

    if trends:
        for trend in trends[:3]:
            with st.container():
                col1, col2 = st.columns([3, 1])

                with col1:
                    # Trend title with strength indicator
                    strength_emoji = "🔥" if trend.strength_score > 0.75 else "📈"
                    st.markdown(f"### {strength_emoji} {trend.topic}")
                    st.caption(trend.explanation)

                with col2:
                    st.metric("Strength", f"{trend.strength_score:.0%}")
                    st.caption(f"{trend.source_count} sources")

                # Show key items
                with st.expander(f"View {len(trend.key_items)} related items"):
                    for item in trend.key_items:
                        st.markdown(f"- [{item.title}]({item.source_url}) ({item.source})")

                st.divider()
    else:
        st.info("No strong trends detected yet. Keep aggregating content!")
```

### Testing Checklist
- [ ] Detects topics from 50+ content items
- [ ] Clusters topics correctly (manual validation)
- [ ] Calculates velocity accurately with historical data
- [ ] Filters single-source noise
- [ ] Scores trends consistently
- [ ] Generates meaningful AI explanations
- [ ] Historical data saves and loads correctly
- [ ] Trend detection completes in <10 seconds
- [ ] Handles edge cases (no historical data, single source, etc.)
- [ ] Trends section renders correctly in newsletter HTML

### Files to Create/Modify

**New Files:**
- `src/ai_newsletter/analysis/trend_detector.py` (~500 lines)
- `src/ai_newsletter/models/trend.py` (~80 lines)
- `src/ai_newsletter/utils/historical_storage.py` (~150 lines)
- `tests/unit/test_trend_detector.py` (~300 lines)

**Modified Files:**
- `src/ai_newsletter/generators/newsletter_generator.py` (~100 line changes)
- `src/streamlit_app.py` - content_scraper_tab() (~80 lines added)
- `src/ai_newsletter/generators/templates/default.html` (~50 lines added)

### Dependencies
- `scikit-learn` for clustering and TF-IDF
- `nltk` or `spacy` for text processing
- Existing OpenAI/OpenRouter for explanations

### Estimated Effort
- **Topic Extraction & Clustering:** 8 hours
- **Velocity Calculation:** 4 hours
- **Historical Data Management:** 4 hours
- **AI Explanation Generation:** 4 hours
- **Integration with Generator:** 4 hours
- **UI Implementation:** 4 hours
- **Testing:** 4 hours
- **Total:** 32 hours (~4 days)

---

## Feature 3: Multi-Client Workspace System

**Priority:** P0 - CRITICAL 🔴
**Effort:** 3-4 days
**Sprint:** Sprint 1

### User Story
> "As an agency managing 10 clients, I need isolated configurations for each client so their newsletters, sources, and settings don't interfere with each other."

### Problem Statement
- Current system uses single `config.json` file
- Multiple users/clients would overwrite each other's settings
- No isolation between projects
- Can't scale to agency use case (10+ clients)
- Risk of accidentally sending Client A's newsletter to Client B

### Success Criteria
- [ ] Create and manage multiple workspaces (projects)
- [ ] Each workspace has isolated config, content, and settings
- [ ] Easy workspace switching via dropdown
- [ ] Can clone/export/import workspaces
- [ ] Existing single-user setup migrates to "default" workspace
- [ ] Zero risk of cross-workspace contamination

### Technical Implementation

#### 1. Workspace Directory Structure

```
project_root/
├── workspaces/                    # NEW - All workspace data
│   ├── default/                   # Default workspace (for existing users)
│   │   ├── config.json           # Workspace-specific config
│   │   ├── .env                  # Workspace-specific API keys
│   │   ├── style_profile.json    # Writing style (Feature 1)
│   │   ├── historical_content.json  # Trend detection history (Feature 2)
│   │   ├── feedback_data.json    # User feedback (Feature 4)
│   │   └── cache/                # Scraped content cache
│   │       └── scraped_content_20250120.json
│   ├── client_acme/              # Example client workspace
│   │   ├── config.json
│   │   ├── .env
│   │   └── ...
│   └── client_techcorp/          # Another client
│       └── ...
├── workspace_templates/          # Pre-configured templates (optional)
│   ├── tech_newsletter/
│   │   └── config.json
│   └── marketing_digest/
│       └── config.json
├── config.example.json           # Template for new workspaces
├── .env                          # Root-level .env (fallback)
└── src/
```

#### 2. New Module: `src/ai_newsletter/utils/workspace_manager.py`

**Core Functions:**

```python
class WorkspaceManager:
    """Manages multiple workspaces (client projects)"""

    WORKSPACE_DIR = Path("workspaces")

    @classmethod
    def list_workspaces(cls) -> List[str]:
        """
        List all available workspaces.

        Returns:
            List of workspace names (directory names)
        """
        if not cls.WORKSPACE_DIR.exists():
            cls.WORKSPACE_DIR.mkdir(parents=True)
            cls.create_workspace("default")  # Create default workspace

        return [
            d.name for d in cls.WORKSPACE_DIR.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]

    @classmethod
    def create_workspace(cls,
                        name: str,
                        template: Optional[str] = None,
                        copy_from: Optional[str] = None) -> bool:
        """
        Create a new workspace.

        Args:
            name: Workspace name (alphanumeric, hyphens, underscores only)
            template: Template to use ('tech_newsletter', 'marketing_digest', etc.)
            copy_from: Existing workspace to clone from

        Returns:
            True if successful, False otherwise
        """
        # Validate name
        if not cls._validate_workspace_name(name):
            raise ValueError(f"Invalid workspace name: {name}")

        workspace_dir = cls.WORKSPACE_DIR / name

        # Check if already exists
        if workspace_dir.exists():
            raise ValueError(f"Workspace '{name}' already exists")

        # Create directory
        workspace_dir.mkdir(parents=True)

        # Copy from template or existing workspace
        if copy_from and (cls.WORKSPACE_DIR / copy_from).exists():
            # Clone from existing workspace
            source_dir = cls.WORKSPACE_DIR / copy_from
            shutil.copy(source_dir / "config.json", workspace_dir / "config.json")
            # Don't copy .env for security
        elif template:
            # Copy from template
            template_path = Path("workspace_templates") / template / "config.json"
            if template_path.exists():
                shutil.copy(template_path, workspace_dir / "config.json")
        else:
            # Create from example config
            shutil.copy("config.example.json", workspace_dir / "config.json")

        # Create empty .env
        (workspace_dir / ".env").touch()

        # Create cache directory
        (workspace_dir / "cache").mkdir(exist_ok=True)

        # Create metadata file
        cls._create_workspace_metadata(name)

        return True

    @classmethod
    def delete_workspace(cls, name: str, force: bool = False) -> bool:
        """
        Delete a workspace.

        Args:
            name: Workspace name
            force: Skip safety checks (default: False)

        Returns:
            True if successful
        """
        # Prevent deleting default workspace without force
        if name == "default" and not force:
            raise ValueError("Cannot delete default workspace")

        workspace_dir = cls.WORKSPACE_DIR / name

        if not workspace_dir.exists():
            raise ValueError(f"Workspace '{name}' does not exist")

        # Delete directory and all contents
        shutil.rmtree(workspace_dir)

        return True

    @classmethod
    def get_workspace_path(cls, name: str) -> Path:
        """Get path to workspace directory."""
        return cls.WORKSPACE_DIR / name

    @classmethod
    def load_workspace_config(cls, name: str) -> Settings:
        """
        Load config.json for a workspace.

        Args:
            name: Workspace name

        Returns:
            Settings object
        """
        workspace_dir = cls.get_workspace_path(name)
        config_path = workspace_dir / "config.json"

        if not config_path.exists():
            # Create default config
            cls.create_workspace(name)

        # Load workspace-specific .env
        env_path = workspace_dir / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=True)

        # Load config
        settings = Settings.from_file(str(config_path))

        return settings

    @classmethod
    def save_workspace_config(cls, name: str, settings: Settings) -> bool:
        """
        Save config.json for a workspace.

        Args:
            name: Workspace name
            settings: Settings object to save

        Returns:
            True if successful
        """
        workspace_dir = cls.get_workspace_path(name)
        config_path = workspace_dir / "config.json"

        # Backup existing config
        if config_path.exists():
            backup_path = config_path.with_suffix(
                f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            shutil.copy(config_path, backup_path)

            # Keep only last 5 backups
            cls._cleanup_old_backups(workspace_dir, keep=5)

        # Save new config
        settings.to_file(str(config_path))

        return True

    @classmethod
    def export_workspace(cls, name: str, output_path: Optional[str] = None) -> str:
        """
        Export workspace as a ZIP file.

        Args:
            name: Workspace name
            output_path: Output ZIP path (default: workspace_name.zip)

        Returns:
            Path to created ZIP file
        """
        workspace_dir = cls.get_workspace_path(name)

        if not workspace_dir.exists():
            raise ValueError(f"Workspace '{name}' does not exist")

        # Default output path
        if not output_path:
            output_path = f"{name}_{datetime.now().strftime('%Y%m%d')}.zip"

        # Create ZIP
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in workspace_dir.rglob('*'):
                if file_path.is_file():
                    # Don't include .env for security
                    if file_path.name == '.env':
                        continue

                    arcname = file_path.relative_to(workspace_dir)
                    zipf.write(file_path, arcname)

        return output_path

    @classmethod
    def import_workspace(cls,
                        zip_path: str,
                        name: Optional[str] = None) -> str:
        """
        Import workspace from ZIP file.

        Args:
            zip_path: Path to ZIP file
            name: Workspace name (default: extracted from ZIP)

        Returns:
            Name of created workspace
        """
        # Generate name if not provided
        if not name:
            name = Path(zip_path).stem.split('_')[0]  # Remove timestamp

        # Ensure unique name
        base_name = name
        counter = 1
        while (cls.WORKSPACE_DIR / name).exists():
            name = f"{base_name}_{counter}"
            counter += 1

        workspace_dir = cls.WORKSPACE_DIR / name
        workspace_dir.mkdir(parents=True)

        # Extract ZIP
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(workspace_dir)

        # Create empty .env (not included in export)
        (workspace_dir / ".env").touch()

        return name

    @classmethod
    def _validate_workspace_name(cls, name: str) -> bool:
        """
        Validate workspace name (prevent directory traversal attacks).

        Args:
            name: Workspace name to validate

        Returns:
            True if valid
        """
        # Only allow alphanumeric, hyphens, underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            return False

        # Prevent path traversal
        if '..' in name or '/' in name or '\\' in name:
            return False

        # Max length
        if len(name) > 50:
            return False

        return True

    @classmethod
    def _create_workspace_metadata(cls, name: str):
        """Create metadata file for workspace."""
        workspace_dir = cls.get_workspace_path(name)
        metadata = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "description": "",
            "tags": []
        }

        with open(workspace_dir / "workspace.json", 'w') as f:
            json.dump(metadata, f, indent=2)

    @classmethod
    def _cleanup_old_backups(cls, workspace_dir: Path, keep: int = 5):
        """Delete old backup files, keep only N most recent."""
        backups = sorted(
            workspace_dir.glob("config.backup.*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for backup in backups[keep:]:
            backup.unlink()

    @classmethod
    def migrate_legacy_config(cls):
        """
        Migrate existing config.json to workspaces/default/.

        For backwards compatibility with existing installations.
        """
        legacy_config = Path("config.json")
        default_workspace = cls.WORKSPACE_DIR / "default"

        # Only migrate if legacy config exists and default doesn't
        if legacy_config.exists() and not default_workspace.exists():
            print("🔄 Migrating existing configuration to workspace system...")

            # Create default workspace directory
            default_workspace.mkdir(parents=True)

            # Move config.json
            shutil.move(str(legacy_config), str(default_workspace / "config.json"))

            # Copy .env (keep original for backwards compatibility)
            if Path(".env").exists():
                shutil.copy(".env", str(default_workspace / ".env"))

            # Create metadata
            cls._create_workspace_metadata("default")

            print("✅ Migration complete! Your settings are in 'default' workspace.")
```

#### 3. Update Settings Module

**Modify:** `src/ai_newsletter/config/settings.py`

```python
def get_settings(
    workspace: str = 'default',
    config_path: Optional[str] = None,
    use_env: bool = True
) -> Settings:
    """
    Get settings for a specific workspace.

    Args:
        workspace: Workspace name (default: 'default')
        config_path: Override config path (optional)
        use_env: Load from environment variables (default: True)

    Returns:
        Settings instance for the workspace
    """
    global _settings

    # Use WorkspaceManager to load settings
    if workspace != 'default' or config_path is None:
        from ..utils.workspace_manager import WorkspaceManager
        settings = WorkspaceManager.load_workspace_config(workspace)
    else:
        # Legacy path
        if use_env:
            settings = Settings.from_env()
        else:
            settings = Settings()

        if config_path and os.path.exists(config_path):
            file_settings = Settings.from_file(config_path)
            # Merge...

    _settings = settings
    return _settings
```

#### 4. Streamlit UI Changes

**Location:** Sidebar (visible on all tabs)

```python
def main():
    st.set_page_config(...)

    # === WORKSPACE SELECTOR (NEW - TOP OF SIDEBAR) ===
    with st.sidebar:
        st.markdown("### 📁 Workspace")

        # Migrate legacy config if needed
        from ai_newsletter.utils.workspace_manager import WorkspaceManager
        WorkspaceManager.migrate_legacy_config()

        # Get available workspaces
        workspaces = WorkspaceManager.list_workspaces()

        # Initialize session state
        if 'current_workspace' not in st.session_state:
            st.session_state.current_workspace = 'default'

        # Workspace selector
        selected_workspace = st.selectbox(
            "Active Workspace",
            options=workspaces,
            index=workspaces.index(st.session_state.current_workspace)
                  if st.session_state.current_workspace in workspaces else 0,
            help="Each workspace has independent configuration and content",
            label_visibility="collapsed"
        )

        # Update session state if changed
        if selected_workspace != st.session_state.current_workspace:
            st.session_state.current_workspace = selected_workspace
            # Clear cached content when switching workspaces
            if 'content_items' in st.session_state:
                del st.session_state.content_items
            st.rerun()

        # Workspace actions
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕", help="Create new workspace"):
                st.session_state.show_new_workspace = True
        with col2:
            if st.button("⚙️", help="Manage workspaces"):
                st.session_state.show_workspace_manager = True
        with col3:
            if st.button("📤", help="Export workspace"):
                st.session_state.show_export_workspace = True

        st.markdown("---")

    # NEW WORKSPACE MODAL
    if st.session_state.get('show_new_workspace', False):
        create_workspace_modal()

    # WORKSPACE MANAGER MODAL
    if st.session_state.get('show_workspace_manager', False):
        workspace_manager_modal()

    # EXPORT MODAL
    if st.session_state.get('show_export_workspace', False):
        export_workspace_modal()

    # Load settings for current workspace
    settings = get_settings(workspace=st.session_state.current_workspace)

    # Show workspace indicator in all tabs
    st.caption(f"📁 Workspace: **{st.session_state.current_workspace}**")

    # Rest of app (tabs)...
```

**Modal Functions:**

```python
def create_workspace_modal():
    """Modal for creating new workspace"""
    st.markdown("### ➕ Create New Workspace")

    with st.form("new_workspace_form"):
        new_name = st.text_input(
            "Workspace Name",
            placeholder="e.g., client-acme",
            help="Use lowercase, hyphens allowed. No spaces or special characters."
        )

        copy_from = st.selectbox(
            "Copy settings from",
            options=['<blank template>'] + WorkspaceManager.list_workspaces(),
            help="Start with empty config or clone existing workspace"
        )

        description = st.text_area(
            "Description (optional)",
            placeholder="e.g., Tech newsletter for ACME Corp"
        )

        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Create", type="primary")
        with col2:
            cancel = st.form_submit_button("Cancel")

        if submit:
            try:
                # Validate name
                if not new_name:
                    st.error("Workspace name is required")
                    return

                # Create workspace
                copy_source = None if copy_from == '<blank template>' else copy_from
                WorkspaceManager.create_workspace(new_name, copy_from=copy_source)

                # Update description if provided
                if description:
                    workspace_dir = WorkspaceManager.get_workspace_path(new_name)
                    with open(workspace_dir / "workspace.json", 'r+') as f:
                        metadata = json.load(f)
                        metadata['description'] = description
                        f.seek(0)
                        json.dump(metadata, f, indent=2)
                        f.truncate()

                st.success(f"✅ Created workspace: {new_name}")
                st.session_state.current_workspace = new_name
                st.session_state.show_new_workspace = False
                st.rerun()

            except ValueError as e:
                st.error(f"❌ Error: {e}")

        if cancel:
            st.session_state.show_new_workspace = False
            st.rerun()

def workspace_manager_modal():
    """Modal for managing workspaces"""
    st.markdown("### ⚙️ Workspace Manager")

    workspaces = WorkspaceManager.list_workspaces()

    for workspace in workspaces:
        with st.expander(f"📁 {workspace}", expanded=(workspace == st.session_state.current_workspace)):
            # Load metadata
            workspace_dir = WorkspaceManager.get_workspace_path(workspace)
            metadata_path = workspace_dir / "workspace.json"

            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)

                st.caption(f"Created: {metadata.get('created_at', 'Unknown')}")
                if metadata.get('description'):
                    st.write(metadata['description'])

            # Actions
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(f"🔄 Switch", key=f"switch_{workspace}"):
                    st.session_state.current_workspace = workspace
                    st.session_state.show_workspace_manager = False
                    st.rerun()

            with col2:
                if st.button(f"📤 Export", key=f"export_{workspace}"):
                    zip_path = WorkspaceManager.export_workspace(workspace)
                    with open(zip_path, 'rb') as f:
                        st.download_button(
                            "💾 Download",
                            data=f,
                            file_name=f"{workspace}.zip",
                            mime="application/zip"
                        )

            with col3:
                if workspace != 'default':
                    if st.button(f"🗑️ Delete", key=f"delete_{workspace}"):
                        if st.session_state.get(f'confirm_delete_{workspace}', False):
                            WorkspaceManager.delete_workspace(workspace)
                            if st.session_state.current_workspace == workspace:
                                st.session_state.current_workspace = 'default'
                            st.rerun()
                        else:
                            st.session_state[f'confirm_delete_{workspace}'] = True
                            st.warning("Click again to confirm deletion")

    if st.button("Close"):
        st.session_state.show_workspace_manager = False
        st.rerun()

def export_workspace_modal():
    """Modal for exporting workspace"""
    st.markdown("### 📤 Export Workspace")

    workspace = st.session_state.current_workspace

    st.info(f"Exporting workspace: **{workspace}**")
    st.caption("The export will include configuration and data, but NOT API keys (.env file).")

    if st.button("📦 Create Export"):
        with st.spinner("Creating export..."):
            zip_path = WorkspaceManager.export_workspace(workspace)

        with open(zip_path, 'rb') as f:
            st.download_button(
                "💾 Download Export",
                data=f,
                file_name=f"{workspace}_{datetime.now().strftime('%Y%m%d')}.zip",
                mime="application/zip",
                type="primary"
            )

        st.success("✅ Export created!")

    if st.button("Close"):
        st.session_state.show_export_workspace = False
        st.rerun()
```

### Testing Checklist
- [ ] Can create new workspace with unique name
- [ ] Can create workspace by cloning existing one
- [ ] Can delete workspace (except default)
- [ ] Can switch between workspaces
- [ ] Each workspace has isolated config.json
- [ ] Each workspace has isolated .env file
- [ ] Content doesn't leak between workspaces
- [ ] Legacy config.json migrates to default workspace
- [ ] Can export workspace as ZIP
- [ ] Can import workspace from ZIP
- [ ] Workspace validation prevents directory traversal
- [ ] Backups are created on config save
- [ ] Old backups are cleaned up (keep 5)

### Files to Create/Modify

**New Files:**
- `src/ai_newsletter/utils/workspace_manager.py` (~500 lines)
- `tests/unit/test_workspace_manager.py` (~300 lines)

**Modified Files:**
- `src/ai_newsletter/config/settings.py` (~50 line changes)
- `src/streamlit_app.py` - main() and modal functions (~300 lines added)
- `.gitignore` - add `workspaces/*/.env` and `workspaces/*/cache/`

### Estimated Effort
- **WorkspaceManager Module:** 12 hours
- **Settings Integration:** 4 hours
- **UI Implementation (Sidebar + Modals):** 8 hours
- **Migration Logic:** 2 hours
- **Testing:** 6 hours
- **Total:** 32 hours (~4 days)

---

## Feature 4: Feedback Loop

**Priority:** P1 - HIGH 🟡
**Effort:** 2-3 days
**Sprint:** Sprint 3

### User Story
> "As a newsletter creator, I want the AI to learn from my edits so that future newsletters require less manual correction."

### Problem Statement
- AI generates newsletters but doesn't learn from user feedback
- No way to indicate which content items are good/bad
- System can't improve content selection over time
- Users must repeatedly edit the same issues

### Success Criteria
- [ ] User can rate content items (👍/👎)
- [ ] System tracks which items user keeps vs deletes
- [ ] AI learns from feedback to adjust content scoring
- [ ] Future newsletters show measurable improvement
- [ ] Feedback data persists across sessions

### Technical Implementation

#### 1. Feedback Data Structure

```python
@dataclass
class FeedbackItem:
    """Represents user feedback on a content item"""

    # Content identification
    content_id: str  # Unique ID for the content item
    title: str
    source: str
    source_url: str

    # Feedback
    rating: Optional[str]  # "positive", "negative", "neutral"
    included_in_final: bool  # Did user keep it in final newsletter?

    # Edit tracking
    original_summary: str
    edited_summary: Optional[str]
    edit_distance: float  # 0.0 (no edits) to 1.0 (completely rewritten)

    # Context
    workspace: str
    newsletter_date: datetime
    feedback_date: datetime

    # Learning signals
    engagement_prediction: Optional[float]  # Predicted engagement
    actual_engagement: Optional[float]  # Actual engagement (if tracked)

@dataclass
class NewsletterFeedback:
    """Feedback for an entire newsletter"""

    newsletter_id: str
    workspace: str
    generated_at: datetime

    # Overall feedback
    overall_rating: Optional[int]  # 1-5 stars
    time_to_finalize: Optional[int]  # minutes

    # Item feedback
    items: List[FeedbackItem]

    # Changes made
    items_added: int
    items_removed: int
    items_edited: int

    # User notes
    notes: Optional[str]
```

#### 2. New Module: `src/ai_newsletter/learning/feedback_tracker.py`

```python
class FeedbackTracker:
    """Tracks and learns from user feedback"""

    def __init__(self, workspace: str):
        self.workspace = workspace
        self.feedback_file = WorkspaceManager.get_workspace_path(workspace) / "feedback_data.json"
        self.feedback_history = self._load_feedback_history()

    def record_item_feedback(self,
                            content_item: ContentItem,
                            rating: Optional[str] = None,
                            included: bool = True,
                            edited_summary: Optional[str] = None):
        """
        Record feedback for a single content item.
        """
        feedback = FeedbackItem(
            content_id=self._generate_content_id(content_item),
            title=content_item.title,
            source=content_item.source,
            source_url=content_item.source_url,
            rating=rating,
            included_in_final=included,
            original_summary=content_item.summary or "",
            edited_summary=edited_summary,
            edit_distance=self._calculate_edit_distance(
                content_item.summary or "",
                edited_summary or content_item.summary or ""
            ),
            workspace=self.workspace,
            newsletter_date=datetime.now(),
            feedback_date=datetime.now(),
            engagement_prediction=None,
            actual_engagement=None
        )

        self.feedback_history.append(feedback)
        self._save_feedback_history()

    def get_source_quality_scores(self) -> Dict[str, float]:
        """
        Calculate quality scores for each source based on feedback.

        Returns:
            Dict mapping source name to quality score (0.0 to 1.0)
        """
        source_feedback = defaultdict(list)

        for feedback in self.feedback_history:
            if feedback.rating:
                score = 1.0 if feedback.rating == "positive" else 0.0
                source_feedback[feedback.source].append(score)
            elif feedback.included_in_final:
                source_feedback[feedback.source].append(0.5)  # Neutral if kept

        # Calculate average scores
        source_scores = {}
        for source, scores in source_feedback.items():
            source_scores[source] = sum(scores) / len(scores) if scores else 0.5

        return source_scores

    def get_content_preferences(self) -> Dict[str, Any]:
        """
        Extract learned preferences from feedback history.

        Returns:
            Dict with preference patterns
        """
        preferences = {
            'preferred_sources': [],
            'avoided_topics': [],
            'preferred_content_length': 0,
            'preferred_recency': 0,  # hours
        }

        # Analyze positive feedback
        positive_items = [f for f in self.feedback_history if f.rating == "positive"]
        negative_items = [f for f in self.feedback_history if f.rating == "negative"]

        # Preferred sources
        source_scores = self.get_source_quality_scores()
        preferences['preferred_sources'] = [
            source for source, score in sorted(source_scores.items(), key=lambda x: x[1], reverse=True)
            if score > 0.6
        ]

        # Content length preference (based on edit distance)
        if positive_items:
            avg_edits = sum(f.edit_distance for f in positive_items) / len(positive_items)
            preferences['acceptable_edit_level'] = avg_edits

        return preferences

    def adjust_content_scoring(self,
                               items: List[ContentItem]) -> List[ContentItem]:
        """
        Adjust content scores based on learned preferences.

        Args:
            items: List of content items with initial scores

        Returns:
            Items with adjusted scores
        """
        source_scores = self.get_source_quality_scores()
        preferences = self.get_content_preferences()

        for item in items:
            # Adjust score based on source quality
            if item.source in source_scores:
                source_multiplier = source_scores[item.source]
                item.score = int(item.score * source_multiplier)

            # Boost preferred sources
            if item.source in preferences['preferred_sources']:
                item.score = int(item.score * 1.2)

        return items

    def _calculate_edit_distance(self, original: str, edited: str) -> float:
        """
        Calculate normalized edit distance (0.0 = no edits, 1.0 = complete rewrite).
        """
        if not original or not edited:
            return 0.0

        # Levenshtein distance
        distance = levenshtein_distance(original, edited)
        max_len = max(len(original), len(edited))

        return distance / max_len if max_len > 0 else 0.0

    def _generate_content_id(self, item: ContentItem) -> str:
        """Generate unique ID for content item."""
        return hashlib.md5(f"{item.source}:{item.source_url}".encode()).hexdigest()

    def _load_feedback_history(self) -> List[FeedbackItem]:
        """Load feedback history from file."""
        if not self.feedback_file.exists():
            return []

        with open(self.feedback_file, 'r') as f:
            data = json.load(f)

        return [FeedbackItem(**item) for item in data]

    def _save_feedback_history(self):
        """Save feedback history to file."""
        with open(self.feedback_file, 'w') as f:
            json.dump(
                [asdict(item) for item in self.feedback_history],
                f,
                indent=2,
                default=str  # Handle datetime serialization
            )
```

#### 3. Integration with NewsletterGenerator

**Modify:** `src/ai_newsletter/generators/newsletter_generator.py`

```python
class NewsletterGenerator:
    def _select_diverse_content(self, items, max_items, max_per_source):
        # EXISTING: Score items
        scored_items = [(self._score_content_item(item), item) for item in items]

        # NEW: Adjust scores based on feedback
        workspace = st.session_state.get('current_workspace', 'default')
        feedback_tracker = FeedbackTracker(workspace)

        # Apply learned preferences
        adjusted_items = []
        for score, item in scored_items:
            # Get source quality from feedback
            source_scores = feedback_tracker.get_source_quality_scores()
            if item.source in source_scores:
                score *= source_scores[item.source]

            adjusted_items.append((score, item))

        # Re-sort with adjusted scores
        adjusted_items.sort(key=lambda x: x[0], reverse=True)

        # Continue with selection...
```

### UI Changes

#### Location 1: Newsletter Generator Tab - Item Rating

```python
def newsletter_generator_tab(settings, workspace):
    # ... existing code ...

    # Display newsletter preview
    if 'newsletter_html' in st.session_state:
        st.subheader("📄 Newsletter Preview")

        # NEW: Add feedback collection
        st.markdown("### ⭐ Rate This Newsletter")
        col1, col2 = st.columns([3, 1])

        with col1:
            overall_rating = st.slider(
                "Overall quality",
                min_value=1,
                max_value=5,
                value=3,
                help="How satisfied are you with this draft?"
            )

        with col2:
            time_spent = st.number_input(
                "Minutes to finalize",
                min_value=0,
                max_value=180,
                value=20
            )

        # Item-level feedback
        st.markdown("### 📋 Rate Individual Items")
        st.caption("Help improve future newsletters by rating each item")

        feedback_tracker = FeedbackTracker(workspace)

        for idx, item in enumerate(st.session_state.content_items[:10]):
            with st.container():
                col1, col2, col3 = st.columns([6, 1, 1])

                with col1:
                    st.markdown(f"**{item.title}**")
                    st.caption(f"{item.source} • {item.score} points")

                with col2:
                    if st.button("👍", key=f"like_{idx}"):
                        feedback_tracker.record_item_feedback(
                            item,
                            rating="positive",
                            included=True
                        )
                        st.success("Feedback saved!")

                with col3:
                    if st.button("👎", key=f"dislike_{idx}"):
                        feedback_tracker.record_item_feedback(
                            item,
                            rating="negative",
                            included=False
                        )
                        st.info("Feedback saved!")

                st.divider()

        # Show learning stats
        with st.expander("📊 Learning Stats"):
            source_scores = feedback_tracker.get_source_quality_scores()
            preferences = feedback_tracker.get_content_preferences()

            st.markdown("**Source Quality Scores:**")
            for source, score in sorted(source_scores.items(), key=lambda x: x[1], reverse=True):
                st.progress(score, text=f"{source}: {score:.0%}")

            st.markdown("**Preferred Sources:**")
            st.write(", ".join(preferences['preferred_sources']) or "Not enough data yet")
```

#### Location 2: Settings Tab - Feedback Dashboard

```python
def settings_tab(settings, workspace):
    # ... existing sections ...

    with st.expander("📊 Feedback & Learning", expanded=False):
        feedback_tracker = FeedbackTracker(workspace)

        st.markdown("### Learning from Your Feedback")

        feedback_count = len(feedback_tracker.feedback_history)

        if feedback_count == 0:
            st.info("No feedback data yet. Start rating newsletters to help the AI learn!")
        else:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Feedback Items", feedback_count)

            with col2:
                positive_count = sum(
                    1 for f in feedback_tracker.feedback_history
                    if f.rating == "positive"
                )
                st.metric("Positive Ratings", positive_count)

            with col3:
                negative_count = sum(
                    1 for f in feedback_tracker.feedback_history
                    if f.rating == "negative"
                )
                st.metric("Negative Ratings", negative_count)

            # Source quality scores
            st.markdown("### Source Performance")
            source_scores = feedback_tracker.get_source_quality_scores()

            for source, score in sorted(source_scores.items(), key=lambda x: x[1], reverse=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.progress(score, text=source)
                with col2:
                    st.caption(f"{score:.0%}")

            # Reset feedback
            if st.button("🔄 Reset Learning Data"):
                if st.button("Confirm Reset", type="secondary"):
                    feedback_tracker.feedback_file.unlink()
                    st.success("Feedback data reset!")
                    st.rerun()
```

### Testing Checklist
- [ ] Can record positive/negative feedback
- [ ] Feedback persists across sessions
- [ ] Source quality scores calculate correctly
- [ ] Content scoring adjusts based on feedback
- [ ] Multiple workspaces have separate feedback
- [ ] Feedback dashboard shows accurate stats
- [ ] Can reset feedback data
- [ ] Performance: feedback loading is fast (<1s)

### Files to Create/Modify

**New Files:**
- `src/ai_newsletter/learning/feedback_tracker.py` (~400 lines)
- `src/ai_newsletter/models/feedback.py` (~100 lines)
- `tests/unit/test_feedback_tracker.py` (~250 lines)

**Modified Files:**
- `src/ai_newsletter/generators/newsletter_generator.py` (~50 line changes)
- `src/streamlit_app.py` - newsletter_generator_tab() and settings_tab() (~150 lines added)

### Dependencies
- `python-Levenshtein` for edit distance calculation (or use difflib)

### Estimated Effort
- **FeedbackTracker Module:** 8 hours
- **Integration with Generator:** 4 hours
- **UI Implementation:** 6 hours
- **Testing:** 4 hours
- **Total:** 22 hours (~2.75 days)

---

## Feature 5: Engagement Analytics

**Priority:** P1 - HIGH 🟡
**Effort:** 3-4 days
**Sprint:** Sprint 3

### User Story
> "As a newsletter creator, I want to track open rates and click-through rates so I can prove ROI and optimize content."

### Problem Statement
- System sends emails but doesn't track engagement
- No visibility into which content performs best
- Can't prove "2× engagement uplift" KPI from product brief
- No data to optimize content selection

### Success Criteria
- [ ] Track email open rates (via tracking pixel)
- [ ] Track link click-through rates (via UTM parameters)
- [ ] Show analytics dashboard with key metrics
- [ ] Identify top-performing content types and sources
- [ ] Export analytics data (CSV/PDF)
- [ ] Trend analysis (week-over-week, month-over-month)

### Technical Implementation

#### 1. Analytics Data Structure

```python
@dataclass
class EmailEvent:
    """Represents an email engagement event"""

    # Email identification
    newsletter_id: str
    workspace: str
    recipient: str

    # Event details
    event_type: str  # "sent", "opened", "clicked", "bounced"
    event_time: datetime

    # Click details (if event_type == "clicked")
    clicked_url: Optional[str]
    content_item_id: Optional[str]  # Which content item was clicked

    # Context
    user_agent: Optional[str]
    ip_address: Optional[str]
    location: Optional[str]  # City, Country (from IP)

@dataclass
class NewsletterAnalytics:
    """Analytics for a single newsletter"""

    newsletter_id: str
    workspace: str
    sent_at: datetime

    # Delivery stats
    sent_count: int
    delivered_count: int
    bounced_count: int

    # Engagement stats
    opened_count: int
    unique_opens: int
    open_rate: float

    clicked_count: int
    unique_clicks: int
    click_rate: float
    click_to_open_rate: float

    # Content performance
    top_clicked_items: List[Dict[str, Any]]  # [(content_id, clicks), ...]
    top_sources: List[Dict[str, Any]]  # [(source, clicks), ...]

    # Timing
    avg_time_to_open: Optional[timedelta]
    avg_time_to_click: Optional[timedelta]
```

#### 2. New Module: `src/ai_newsletter/analytics/tracker.py`

```python
class AnalyticsTracker:
    """Tracks email engagement and generates analytics"""

    def __init__(self, workspace: str):
        self.workspace = workspace
        self.events_file = WorkspaceManager.get_workspace_path(workspace) / "analytics_events.json"
        self.events = self._load_events()

    def generate_tracking_pixel(self, newsletter_id: str, recipient: str) -> str:
        """
        Generate tracking pixel URL for email open tracking.

        Returns:
            URL to 1×1 transparent pixel image
        """
        # Encode parameters
        params = base64.urlsafe_b64encode(
            json.dumps({
                'newsletter_id': newsletter_id,
                'workspace': self.workspace,
                'recipient': recipient
            }).encode()
        ).decode()

        # Return tracking URL (would point to your tracking endpoint)
        return f"https://yourdomain.com/track/open/{params}.png"

    def generate_tracked_link(self,
                             newsletter_id: str,
                             recipient: str,
                             original_url: str,
                             content_item_id: str) -> str:
        """
        Generate tracked link with UTM parameters.

        Returns:
            URL with tracking parameters
        """
        parsed = urlparse(original_url)
        params = parse_qs(parsed.query)

        # Add UTM parameters
        params.update({
            'utm_source': 'newsletter',
            'utm_medium': 'email',
            'utm_campaign': newsletter_id,
            'utm_content': content_item_id,
            # Add tracking redirect parameter
            'track': base64.urlsafe_b64encode(
                json.dumps({
                    'newsletter_id': newsletter_id,
                    'workspace': self.workspace,
                    'recipient': recipient,
                    'content_item_id': content_item_id
                }).encode()
            ).decode()
        })

        # Rebuild URL
        new_query = urlencode(params, doseq=True)
        tracked_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))

        return tracked_url

    def record_event(self,
                    newsletter_id: str,
                    recipient: str,
                    event_type: str,
                    clicked_url: Optional[str] = None,
                    content_item_id: Optional[str] = None,
                    user_agent: Optional[str] = None,
                    ip_address: Optional[str] = None):
        """
        Record an engagement event.
        """
        event = EmailEvent(
            newsletter_id=newsletter_id,
            workspace=self.workspace,
            recipient=recipient,
            event_type=event_type,
            event_time=datetime.now(),
            clicked_url=clicked_url,
            content_item_id=content_item_id,
            user_agent=user_agent,
            ip_address=ip_address,
            location=self._get_location_from_ip(ip_address) if ip_address else None
        )

        self.events.append(event)
        self._save_events()

    def get_newsletter_analytics(self, newsletter_id: str) -> NewsletterAnalytics:
        """
        Get analytics for a specific newsletter.
        """
        # Filter events for this newsletter
        newsletter_events = [
            e for e in self.events
            if e.newsletter_id == newsletter_id
        ]

        if not newsletter_events:
            return None

        # Calculate metrics
        sent_events = [e for e in newsletter_events if e.event_type == "sent"]
        open_events = [e for e in newsletter_events if e.event_type == "opened"]
        click_events = [e for e in newsletter_events if e.event_type == "clicked"]
        bounce_events = [e for e in newsletter_events if e.event_type == "bounced"]

        sent_count = len(sent_events)
        delivered_count = sent_count - len(bounce_events)
        opened_count = len(open_events)
        unique_opens = len(set(e.recipient for e in open_events))
        clicked_count = len(click_events)
        unique_clicks = len(set(e.recipient for e in click_events))

        open_rate = unique_opens / delivered_count if delivered_count > 0 else 0
        click_rate = unique_clicks / delivered_count if delivered_count > 0 else 0
        click_to_open_rate = unique_clicks / unique_opens if unique_opens > 0 else 0

        # Top clicked items
        click_counts = Counter(
            e.content_item_id for e in click_events
            if e.content_item_id
        )
        top_clicked_items = [
            {'content_id': cid, 'clicks': count}
            for cid, count in click_counts.most_common(10)
        ]

        # Calculate timing
        if sent_events and open_events:
            sent_time = min(e.event_time for e in sent_events)
            open_times = [e.event_time for e in open_events]
            avg_time_to_open = sum(
                (ot - sent_time for ot in open_times),
                timedelta()
            ) / len(open_times)
        else:
            avg_time_to_open = None

        return NewsletterAnalytics(
            newsletter_id=newsletter_id,
            workspace=self.workspace,
            sent_at=min(e.event_time for e in sent_events) if sent_events else datetime.now(),
            sent_count=sent_count,
            delivered_count=delivered_count,
            bounced_count=len(bounce_events),
            opened_count=opened_count,
            unique_opens=unique_opens,
            open_rate=open_rate,
            clicked_count=clicked_count,
            unique_clicks=unique_clicks,
            click_rate=click_rate,
            click_to_open_rate=click_to_open_rate,
            top_clicked_items=top_clicked_items,
            top_sources=[],
            avg_time_to_open=avg_time_to_open,
            avg_time_to_click=None
        )

    def get_aggregate_analytics(self,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get aggregate analytics across multiple newsletters.
        """
        # Filter events by date range
        events = self.events
        if start_date:
            events = [e for e in events if e.event_time >= start_date]
        if end_date:
            events = [e for e in events if e.event_time <= end_date]

        # Calculate aggregate metrics
        total_sent = len([e for e in events if e.event_type == "sent"])
        total_opens = len([e for e in events if e.event_type == "opened"])
        total_clicks = len([e for e in events if e.event_type == "clicked"])

        unique_opens = len(set(
            (e.newsletter_id, e.recipient)
            for e in events if e.event_type == "opened"
        ))
        unique_clicks = len(set(
            (e.newsletter_id, e.recipient)
            for e in events if e.event_type == "clicked"
        ))

        avg_open_rate = unique_opens / total_sent if total_sent > 0 else 0
        avg_click_rate = unique_clicks / total_sent if total_sent > 0 else 0

        return {
            'total_newsletters': len(set(e.newsletter_id for e in events)),
            'total_sent': total_sent,
            'total_opens': total_opens,
            'total_clicks': total_clicks,
            'unique_opens': unique_opens,
            'unique_clicks': unique_clicks,
            'avg_open_rate': avg_open_rate,
            'avg_click_rate': avg_click_rate,
            'date_range': {
                'start': start_date.isoformat() if start_date else None,
                'end': end_date.isoformat() if end_date else None
            }
        }

    def _get_location_from_ip(self, ip_address: str) -> str:
        """Get location from IP address (using ipapi or similar)."""
        # TODO: Integrate with IP geolocation service
        return "Unknown"

    def _load_events(self) -> List[EmailEvent]:
        """Load events from file."""
        if not self.events_file.exists():
            return []

        with open(self.events_file, 'r') as f:
            data = json.load(f)

        return [EmailEvent(**e) for e in data]

    def _save_events(self):
        """Save events to file."""
        with open(self.events_file, 'w') as f:
            json.dump(
                [asdict(e) for e in self.events],
                f,
                indent=2,
                default=str
            )
```

#### 3. Integration with Email Sender

**Modify:** `src/ai_newsletter/delivery/email_sender.py`

```python
class EmailSender:
    def send_newsletter(self, recipient, subject, html_content, ...):
        # Generate newsletter ID
        newsletter_id = hashlib.md5(
            f"{subject}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        # NEW: Add tracking pixel to HTML
        tracker = AnalyticsTracker(workspace)
        tracking_pixel_url = tracker.generate_tracking_pixel(newsletter_id, recipient)

        html_with_tracking = html_content + f'''
        <img src="{tracking_pixel_url}" width="1" height="1" alt="" />
        '''

        # NEW: Add tracking to all links
        html_with_tracking = self._add_tracking_to_links(
            html_with_tracking,
            newsletter_id,
            recipient,
            tracker
        )

        # Send email
        success = self._send_email(recipient, subject, html_with_tracking)

        # Record sent event
        if success:
            tracker.record_event(
                newsletter_id=newsletter_id,
                recipient=recipient,
                event_type="sent"
            )

        return success

    def _add_tracking_to_links(self, html, newsletter_id, recipient, tracker):
        """Add tracking parameters to all links in HTML."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')

        for link in soup.find_all('a', href=True):
            original_url = link['href']

            # Skip email/tel links
            if original_url.startswith(('mailto:', 'tel:')):
                continue

            # Generate content ID from link
            content_id = hashlib.md5(original_url.encode()).hexdigest()[:12]

            # Add tracking
            tracked_url = tracker.generate_tracked_link(
                newsletter_id,
                recipient,
                original_url,
                content_id
            )

            link['href'] = tracked_url

        return str(soup)
```

#### 4. Tracking Endpoint (Flask/FastAPI)

**New file:** `src/ai_newsletter/analytics/tracking_server.py`

```python
from flask import Flask, request, send_file, redirect
import io

app = Flask(__name__)

@app.route('/track/open/<encoded_params>.png')
def track_open(encoded_params):
    """Handle tracking pixel requests (email opens)."""
    try:
        # Decode parameters
        params = json.loads(
            base64.urlsafe_b64decode(encoded_params.encode()).decode()
        )

        # Record open event
        tracker = AnalyticsTracker(params['workspace'])
        tracker.record_event(
            newsletter_id=params['newsletter_id'],
            recipient=params['recipient'],
            event_type="opened",
            user_agent=request.headers.get('User-Agent'),
            ip_address=request.remote_addr
        )

    except Exception as e:
        print(f"Tracking error: {e}")

    # Return 1×1 transparent PNG
    img = io.BytesIO()
    img.write(base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
    ))
    img.seek(0)
    return send_file(img, mimetype='image/png')

@app.route('/track/click')
def track_click():
    """Handle link click tracking."""
    # Get tracking parameter
    track_param = request.args.get('track')

    if track_param:
        try:
            # Decode parameters
            params = json.loads(
                base64.urlsafe_b64decode(track_param.encode()).decode()
            )

            # Record click event
            tracker = AnalyticsTracker(params['workspace'])
            tracker.record_event(
                newsletter_id=params['newsletter_id'],
                recipient=params['recipient'],
                event_type="clicked",
                clicked_url=request.url,
                content_item_id=params.get('content_item_id'),
                user_agent=request.headers.get('User-Agent'),
                ip_address=request.remote_addr
            )
        except Exception as e:
            print(f"Click tracking error: {e}")

    # Redirect to original URL (remove tracking params)
    clean_params = {k: v for k, v in request.args.items() if k not in ['track']}
    original_url = request.base_url
    if clean_params:
        original_url += '?' + urlencode(clean_params, doseq=True)

    return redirect(original_url, code=302)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### UI Changes

**New Tab:** "📊 Analytics"

```python
def analytics_tab(settings, workspace):
    """Analytics dashboard tab"""
    st.subheader("📊 Engagement Analytics")

    tracker = AnalyticsTracker(workspace)

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30)
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now()
        )

    # Get aggregate analytics
    analytics = tracker.get_aggregate_analytics(
        start_date=datetime.combine(start_date, datetime.min.time()),
        end_date=datetime.combine(end_date, datetime.max.time())
    )

    # Key metrics
    st.markdown("### Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Newsletters",
            analytics['total_newsletters']
        )

    with col2:
        st.metric(
            "Total Sent",
            analytics['total_sent']
        )

    with col3:
        st.metric(
            "Open Rate",
            f"{analytics['avg_open_rate']:.1%}",
            delta="+5.2%" if analytics['avg_open_rate'] > 0.3 else None
        )

    with col4:
        st.metric(
            "Click Rate",
            f"{analytics['avg_click_rate']:.1%}",
            delta="+2.1%" if analytics['avg_click_rate'] > 0.05 else None
        )

    # Charts
    st.markdown("### Performance Over Time")

    # TODO: Create time-series charts
    # - Open rate by day
    # - Click rate by day
    # - Engagement trends

    # Recent newsletters
    st.markdown("### Recent Newsletters")

    newsletter_ids = set(e.newsletter_id for e in tracker.events)

    for newsletter_id in list(newsletter_ids)[:10]:
        newsletter_analytics = tracker.get_newsletter_analytics(newsletter_id)

        if newsletter_analytics:
            with st.expander(f"📧 Newsletter {newsletter_id} • {newsletter_analytics.sent_at.strftime('%b %d, %Y')}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Delivered", newsletter_analytics.delivered_count)
                    st.metric("Opened", f"{newsletter_analytics.open_rate:.1%}")

                with col2:
                    st.metric("Unique Opens", newsletter_analytics.unique_opens)
                    st.metric("Clicked", f"{newsletter_analytics.click_rate:.1%}")

                with col3:
                    st.metric("Unique Clicks", newsletter_analytics.unique_clicks)
                    st.metric("Click-to-Open", f"{newsletter_analytics.click_to_open_rate:.1%}")

                # Top clicked items
                if newsletter_analytics.top_clicked_items:
                    st.markdown("**Top Clicked Items:**")
                    for item in newsletter_analytics.top_clicked_items[:5]:
                        st.write(f"- {item['content_id']}: {item['clicks']} clicks")

    # Export
    st.markdown("### Export Analytics")

    if st.button("📥 Export to CSV"):
        # Create CSV
        csv_data = []
        for event in tracker.events:
            csv_data.append({
                'Newsletter ID': event.newsletter_id,
                'Recipient': event.recipient,
                'Event Type': event.event_type,
                'Event Time': event.event_time,
                'Clicked URL': event.clicked_url or '',
            })

        df = pd.DataFrame(csv_data)
        csv = df.to_csv(index=False)

        st.download_button(
            "💾 Download CSV",
            data=csv,
            file_name=f"analytics_{workspace}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
```

### Testing Checklist
- [ ] Tracking pixel generates correctly
- [ ] Tracking pixel records opens
- [ ] Links have UTM parameters
- [ ] Click tracking works
- [ ] Analytics calculate correctly
- [ ] Dashboard displays metrics
- [ ] Date range filtering works
- [ ] CSV export works
- [ ] Multiple workspaces have separate analytics
- [ ] Tracking server handles high volume

### Files to Create/Modify

**New Files:**
- `src/ai_newsletter/analytics/tracker.py` (~600 lines)
- `src/ai_newsletter/analytics/tracking_server.py` (~150 lines)
- `src/ai_newsletter/models/analytics.py` (~150 lines)
- `tests/unit/test_analytics_tracker.py` (~300 lines)

**Modified Files:**
- `src/ai_newsletter/delivery/email_sender.py` (~100 line changes)
- `src/streamlit_app.py` - new analytics_tab() (~250 lines)
- Add Analytics tab to main tabs

### Dependencies
- `Flask` or `FastAPI` for tracking server
- `BeautifulSoup4` for HTML link parsing
- `requests` for IP geolocation (optional)

### Estimated Effort
- **AnalyticsTracker Module:** 10 hours
- **Tracking Server:** 6 hours
- **Email Sender Integration:** 4 hours
- **UI Dashboard:** 8 hours
- **Testing:** 4 hours
- **Total:** 32 hours (~4 days)

---

## Implementation Order & Timeline

### Sprint 1: Foundation (Week 1)
**Goal:** Enable multi-client agency use case

**Tasks:**
1. ✅ Fix datetime timezone bug (DONE)
2. ✅ Add OpenRouter toggle (DONE)
3. 🔨 Multi-Client Workspace System (3-4 days)
   - WorkspaceManager module
   - UI workspace selector
   - Migration logic
   - Testing

**Deliverable:** Agencies can manage multiple client newsletters

---

### Sprint 2: Core Differentiators (Week 2)
**Goal:** Match user's writing voice and surface trends

**Tasks:**
4. 🔨 Writing Style Trainer (2-3 days)
   - Style analysis algorithm
   - Integration with generator
   - Training UI
   - Testing

5. 🔨 Trends Detection Engine (3-4 days)
   - Topic clustering
   - Velocity detection
   - Trends section in newsletter
   - Testing

**Deliverable:** "70% ready-to-send newsletters that sound like you"

---

### Sprint 3: Learning & Analytics (Week 3)
**Goal:** Continuous improvement and ROI tracking

**Tasks:**
6. 🔨 Feedback Loop (2-3 days)
   - Feedback tracking
   - Learning from edits
   - Source quality scoring
   - Testing

7. 🔨 Engagement Analytics (3-4 days)
   - Tracking infrastructure
   - Analytics dashboard
   - Export functionality
   - Testing

**Deliverable:** "Learns from your feedback & proves ROI"

---

### Sprint 4: Polish & Launch (Week 4)
**Goal:** Production-ready product

**Tasks:**
8. UI/UX improvements
   - Onboarding flow
   - Help documentation
   - Tooltips and guidance
   - Mobile responsiveness

9. Testing & Bug Fixes
   - End-to-end testing
   - Performance optimization
   - Edge case handling
   - Security audit

10. Documentation
    - User guides
    - Video tutorials
    - API documentation
    - Deployment guide

**Deliverable:** Production-ready CreatorPulse matching product vision

---

## Success Metrics

### Quantitative KPIs
- [ ] Newsletter draft acceptance rate: **≥70%** (vs current ~40%)
- [ ] Time to final draft: **<20 minutes** (vs current 90+ minutes)
- [ ] Engagement uplift: **≥2×** (measured via analytics)
- [ ] User retention: **≥80%** after 30 days
- [ ] Agency adoption: **≥5 agencies** with 3+ clients each

### Qualitative Goals
- [ ] Users say: "It sounds like me!"
- [ ] Users say: "I would have missed this trend!"
- [ ] Users say: "It saves me hours every week"
- [ ] Agencies say: "Managing 10+ clients is easy"

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Style training needs 50+ samples (not 20) | Medium | Medium | Progressive disclosure: "Works with 10, better with 50" |
| Trend detection has false positives | High | High | Confidence scoring + human review |
| Tracking server overwhelmed | Medium | Low | Use CDN for pixel, async processing |
| Workspace isolation bug | High | Low | Extensive testing, backups |
| API rate limits (OpenAI/OpenRouter) | Medium | Medium | Caching, rate limiting, fallbacks |

---

## Dependencies & Prerequisites

### Required
- ✅ Python 3.9+
- ✅ Streamlit
- ✅ OpenAI/OpenRouter API access
- 🔲 SMTP or SendGrid for email
- 🔲 Domain for tracking server (analytics)

### Optional
- 🔲 YouTube API key (for YouTube scraping)
- 🔲 X/Twitter API (for X scraping)
- 🔲 IP geolocation service (for analytics)
- 🔲 WhatsApp Business API (future)

---

## Next Steps

### Immediate Actions (Today)
1. Review and approve this roadmap
2. Set up project tracking (GitHub Projects / Jira)
3. Create feature branches:
   - `feature/workspace-system`
   - `feature/style-trainer`
   - `feature/trends-detector`
   - `feature/feedback-loop`
   - `feature/analytics`

### Week 1 Kickoff
1. Start with Workspace System (highest priority)
2. Daily standup: progress check
3. End-of-week demo: working workspaces

### Communication Plan
- Daily: Quick status update
- Weekly: Sprint review + demo
- Blocker protocol: Flag immediately, don't wait

---

## Questions to Resolve

1. **Tracking Server Hosting:** Where will the analytics tracking server run?
   - Option A: Same server as Streamlit
   - Option B: Separate server (recommended for scale)
   - Option C: Use existing analytics service (Mixpanel, Segment)

2. **API Key Security:** How to securely manage API keys for multiple workspaces?
   - Current: .env files per workspace
   - Alternative: Encrypted vault, cloud secret manager

3. **Database vs Files:** Continue with JSON files or migrate to database?
   - Current: JSON files (simple, works for small scale)
   - Future: PostgreSQL/SQLite (better for analytics queries)

4. **Multi-User Auth:** Add authentication/authorization?
   - Current: Single-user desktop app
   - Future: Multi-user with login (required for agencies)

---

## Appendix

### A. File Structure After Implementation

```
project_root/
├── workspaces/
│   ├── default/
│   │   ├── config.json
│   │   ├── .env
│   │   ├── style_profile.json
│   │   ├── historical_content.json
│   │   ├── feedback_data.json
│   │   ├── analytics_events.json
│   │   └── cache/
│   └── client_*/...
├── src/
│   ├── ai_newsletter/
│   │   ├── analytics/
│   │   │   ├── tracker.py
│   │   │   └── tracking_server.py
│   │   ├── generators/
│   │   │   ├── newsletter_generator.py
│   │   │   └── style_trainer.py
│   │   ├── analysis/
│   │   │   └── trend_detector.py
│   │   ├── learning/
│   │   │   └── feedback_tracker.py
│   │   └── utils/
│   │       └── workspace_manager.py
│   └── streamlit_app.py
├── tests/
├── config.example.json
└── IMPLEMENTATION_ROADMAP.md (this file)
```

### B. Estimated Total Effort

| Sprint | Features | Estimated Hours | Days |
|--------|----------|----------------|------|
| Sprint 1 | Workspace System | 32 hours | 4 days |
| Sprint 2 | Style Trainer + Trends | 52 hours | 6.5 days |
| Sprint 3 | Feedback + Analytics | 54 hours | 6.75 days |
| Sprint 4 | Polish + Testing | 40 hours | 5 days |
| **Total** | | **178 hours** | **~22 days** |

**Timeline:** 4-5 weeks with 1 full-time developer

---

## Changelog

- **2025-01-20:** Initial roadmap created
- **[Future dates]:** Track updates here

---

**Status:** ✅ Ready for Implementation
**Approval:** [ ] Pending / [x] Approved
**Start Date:** [To be determined]
