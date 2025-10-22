# Content Persistence Bug Fix - January 22, 2025

## Executive Summary

**Issue:** Newsletter generation fails with "No content found in workspace for the last 7 days" error despite successful content scraping.

**Root Cause:** The `save_content_items()` method in `supabase_client.py` returns an empty array when encountering duplicate content, instead of properly handling the upsert operation.

**Status:** CRITICAL BUG - Blocks core functionality

**Impact:** Users cannot generate newsletters after the first scraping session

---

## Problem Details

### Error Flow

1. User triggers content scraping via frontend
2. Backend successfully scrapes 110+ items from Reddit, X, YouTube
3. Scraper logs: "Duplicate content detected, filtering..."
4. `save_content_items()` returns empty array `[]`
5. API returns: `"total_items": 0` despite scraping 110+ items
6. Newsletter generation attempts to load content
7. `load_content_items()` finds nothing in database
8. Error: "No content found in workspace for the last 7 days"

### Root Cause Analysis

**File:** `src/ai_newsletter/database/supabase_client.py`
**Lines:** 290-300

```python
except Exception as e:
    error_str = str(e).lower()
    if 'unique' in error_str or 'conflict' in error_str:
        # Constraint exists but data conflicts - this is expected
        # Filter out duplicates manually and try again
        print(f"Duplicate content detected, filtering...")
        # For now, just return empty to avoid duplicates
        # The constraint will prevent them from being saved
        return []  # <--- BUG: Returns empty instead of handling upsert
```

The code has a unique constraint:
```sql
CONSTRAINT unique_content_per_workspace
UNIQUE (workspace_id, source, source_url)
```

When `upsert()` is called with `ignore_duplicates=False`, it's supposed to **update** existing records. However, the exception handler catches the conflict and returns `[]` instead.

### Why This Breaks Newsletter Generation

1. **First Scrape:**
   - 110 items scraped
   - No duplicates exist
   - All 110 items inserted successfully
   - ✅ Content available in database

2. **Second Scrape (Minutes Later):**
   - 110 items scraped (same URLs)
   - ALL items detected as duplicates
   - Exception caught, returns `[]`
   - ❌ Database has 110 items, but all have old `scraped_at` timestamps

3. **Newsletter Generation:**
   - Queries content with: `created_at >= (now - 7 days)`
   - Items have `created_at` from days ago (original scrape time)
   - `scraped_at` is NOT updated (because upsert failed)
   - Query returns empty
   - ❌ "No content found" error

---

## Technical Investigation

### Database Schema

**Table:** `content_items`

**Relevant Fields:**
- `workspace_id` (UUID) - Part of unique constraint
- `source` (TEXT) - Part of unique constraint
- `source_url` (TEXT) - Part of unique constraint
- `created_at` (TIMESTAMPTZ) - Content publish date (from source)
- `scraped_at` (TIMESTAMPTZ) - When we fetched it

**Unique Constraint:**
```sql
ALTER TABLE content_items
ADD CONSTRAINT unique_content_per_workspace
UNIQUE (workspace_id, source, source_url);
```

### Current Code Behavior

**Location:** `src/ai_newsletter/database/supabase_client.py:277-304`

```python
def save_content_items(self,
                      workspace_id: str,
                      items: List[ContentItem]) -> List[Dict[str, Any]]:
    """Save scraped content items to database."""
    data = [
        {
            'workspace_id': workspace_id,
            'title': item.title,
            'source': item.source,
            'source_url': item.source_url,
            'created_at': item.created_at.isoformat(),
            'scraped_at': datetime.now().isoformat(),  # <-- Should be updated!
            # ... other fields
        }
        for item in items
    ]

    try:
        result = self.service_client.table('content_items') \
            .upsert(
                data,
                on_conflict='workspace_id,source,source_url',
                ignore_duplicates=False  # Should UPDATE, not ignore
            ) \
            .execute()

        return result.data
    except Exception as e:
        error_str = str(e).lower()
        if 'unique' in error_str or 'conflict' in error_str:
            print(f"Duplicate content detected, filtering...")
            return []  # ❌ BUG: Should handle upsert properly
```

### Expected Behavior

The `upsert()` with `ignore_duplicates=False` should:
1. Insert new items
2. **UPDATE existing items** (including `scraped_at` timestamp)
3. Return ALL processed items (both inserted and updated)

This ensures:
- Fresh content has recent `scraped_at` timestamps
- Newsletter generation can query by `scraped_at` instead of `created_at`
- Content stays "fresh" in the database

---

## Solution Options

### Option 1: Fix Upsert Conflict Handling (Recommended)

**Change:** Remove the exception handler that returns `[]`, let upsert work naturally

```python
try:
    result = self.service_client.table('content_items') \
        .upsert(
            data,
            on_conflict='workspace_id,source,source_url',
            ignore_duplicates=False  # Updates existing records
        ) \
        .execute()

    return result.data
except Exception as e:
    # Log the actual error for debugging
    print(f"Error saving content items: {e}")
    # Re-raise to let caller handle it
    raise
```

**Pros:**
- Simplest fix
- Matches intended behavior
- Updates `scraped_at` timestamps automatically

**Cons:**
- Removes duplicate detection logging
- May expose other upsert issues

### Option 2: Manual Duplicate Filtering

**Change:** Filter out duplicates before upserting

```python
# Check which items already exist
existing_urls = set()
check_result = self.service_client.table('content_items') \
    .select('source_url') \
    .eq('workspace_id', workspace_id) \
    .in_('source_url', [item.source_url for item in items]) \
    .execute()

if check_result.data:
    existing_urls = {row['source_url'] for row in check_result.data}

# Separate new items from updates
new_items = [d for d in data if d['source_url'] not in existing_urls]
update_items = [d for d in data if d['source_url'] in existing_urls]

# Insert new items
if new_items:
    insert_result = self.service_client.table('content_items').insert(new_items).execute()

# Update existing items (just scraped_at timestamp)
if update_items:
    for item_data in update_items:
        self.service_client.table('content_items') \
            .update({'scraped_at': item_data['scraped_at']}) \
            .eq('workspace_id', workspace_id) \
            .eq('source_url', item_data['source_url']) \
            .execute()

return insert_result.data + update_items
```

**Pros:**
- Explicit control over duplicate handling
- Can optimize updates (only timestamp)
- Maintains duplicate detection logging

**Cons:**
- More complex
- Multiple database queries
- Slower performance

### Option 3: Change Newsletter Query Logic

**Change:** Query by `scraped_at` instead of `created_at`

**Location:** `src/ai_newsletter/database/supabase_client.py:323`

```python
# Current (broken with old content):
.gte('created_at', cutoff_date.isoformat())

# Fixed (works with any scraped content):
.gte('scraped_at', cutoff_date.isoformat())
```

**Pros:**
- Simple one-line fix
- Queries recently-scraped content
- Works with duplicate detection

**Cons:**
- Doesn't fix the empty return issue
- Still need to handle upsert properly
- May show same content repeatedly

---

## Recommended Fix: Hybrid Approach

Combine Option 1 + Option 3 for complete solution:

### Step 1: Fix `save_content_items()` Upsert Handling

**File:** `src/ai_newsletter/database/supabase_client.py:277-304`

```python
def save_content_items(self,
                      workspace_id: str,
                      items: List[ContentItem]) -> List[Dict[str, Any]]:
    """
    Save scraped content items to database.

    Uses upsert to handle duplicates:
    - Inserts new items
    - Updates scraped_at timestamp for existing items

    Returns:
        List of saved/updated content data
    """
    if not items:
        return []

    data = [
        {
            'workspace_id': workspace_id,
            'title': item.title,
            'source': item.source,
            'source_url': item.source_url,
            'content': item.content,
            'summary': item.summary,
            'author': item.author,
            'author_url': item.author_url,
            'score': item.score,
            'comments_count': item.comments_count,
            'shares_count': item.shares_count,
            'views_count': item.views_count,
            'image_url': item.image_url,
            'video_url': item.video_url,
            'external_url': item.external_url,
            'tags': item.tags,
            'category': item.category,
            'created_at': item.created_at.isoformat(),
            'scraped_at': datetime.now().isoformat(),
            'metadata': item.metadata
        }
        for item in items
    ]

    try:
        # Upsert with conflict resolution
        # on_conflict parameter ensures we update if duplicate exists
        result = self.service_client.table('content_items') \
            .upsert(
                data,
                on_conflict='workspace_id,source,source_url',
                ignore_duplicates=False  # Update existing records
            ) \
            .execute()

        print(f"✅ Saved/updated {len(result.data)} content items")
        return result.data

    except Exception as e:
        # Log the error for debugging but don't swallow it
        print(f"❌ Error saving content items: {e}")
        print(f"   Attempted to save {len(items)} items")
        print(f"   First item URL: {items[0].source_url if items else 'N/A'}")

        # Check if this is a constraint issue
        error_str = str(e).lower()
        if 'unique' in error_str or 'constraint' in error_str:
            print(f"   Constraint conflict detected - this shouldn't happen with upsert")
            print(f"   Falling back to manual duplicate handling...")

            # Fallback: Try without upsert
            try:
                result = self.service_client.table('content_items').insert(data).execute()
                print(f"✅ Fallback insert succeeded: {len(result.data)} items")
                return result.data
            except Exception as fallback_error:
                print(f"❌ Fallback also failed: {fallback_error}")
                # Return empty as last resort, but log the issue
                print(f"⚠️ WARNING: All content insertion methods failed!")
                return []

        # Re-raise other errors
        raise
```

### Step 2: Update `load_content_items()` Query

**File:** `src/ai_newsletter/database/supabase_client.py:306-367`

```python
def load_content_items(self,
                      workspace_id: str,
                      days: int = 7,
                      source: Optional[str] = None,
                      limit: int = 1000) -> List[ContentItem]:
    """
    Load content items from database.

    Queries by scraped_at (not created_at) to get recently-fetched content.
    This ensures fresh content even when same URLs are re-scraped.
    """
    cutoff_date = datetime.now() - timedelta(days=days)

    query = self.service_client.table('content_items') \
        .select('*') \
        .eq('workspace_id', workspace_id) \
        .gte('scraped_at', cutoff_date.isoformat())  # Changed from created_at
        .order('scraped_at', desc=True) \  # Changed from created_at
        .limit(limit)

    if source:
        query = query.eq('source', source)

    result = query.execute()

    print(f"📊 Loaded {len(result.data)} content items for workspace {workspace_id}")
    print(f"   Query: scraped_at >= {cutoff_date.isoformat()}")

    # Convert to ContentItem objects
    content_items = []
    for item in result.data:
        metadata = item.get('metadata', {})
        metadata['id'] = item['id']

        content_items.append(ContentItem(
            title=item['title'],
            source=item['source'],
            source_url=item['source_url'],
            created_at=datetime.fromisoformat(item['created_at']),
            content=item.get('content'),
            summary=item.get('summary'),
            author=item.get('author'),
            author_url=item.get('author_url'),
            score=item.get('score', 0),
            comments_count=item.get('comments_count', 0),
            shares_count=item.get('shares_count', 0),
            views_count=item.get('views_count', 0),
            image_url=item.get('image_url'),
            video_url=item.get('video_url'),
            external_url=item.get('external_url'),
            tags=item.get('tags', []),
            category=item.get('category'),
            metadata=metadata,
            scraped_at=datetime.fromisoformat(item['scraped_at'])
        ))

    return content_items
```

---

## Testing Plan

### Unit Tests

1. **Test Duplicate Handling:**
```python
def test_save_duplicate_content_items():
    """Verify upsert updates existing items instead of failing."""
    supabase = SupabaseManager()

    # First save
    items1 = [create_test_item(url="https://example.com/post1")]
    result1 = supabase.save_content_items(workspace_id, items1)
    assert len(result1) == 1

    # Second save (same URL)
    time.sleep(1)  # Ensure different scraped_at
    items2 = [create_test_item(url="https://example.com/post1")]
    result2 = supabase.save_content_items(workspace_id, items2)
    assert len(result2) == 1  # Should succeed

    # Verify scraped_at was updated
    loaded = supabase.load_content_items(workspace_id, days=1)
    assert len(loaded) == 1
    assert loaded[0].scraped_at > result1[0]['scraped_at']
```

2. **Test Newsletter Generation:**
```python
def test_newsletter_with_duplicate_scrapes():
    """Verify newsletter generation works after re-scraping."""
    # First scrape
    scrape1 = await content_service.scrape_content(user_id, workspace_id)
    assert scrape1['total_items'] > 0

    # Generate newsletter
    newsletter1 = await newsletter_service.generate_newsletter(workspace_id)
    assert newsletter1 is not None

    # Second scrape (same content)
    scrape2 = await content_service.scrape_content(user_id, workspace_id)
    assert scrape2['total_items'] > 0  # Should not be 0

    # Generate newsletter again
    newsletter2 = await newsletter_service.generate_newsletter(workspace_id)
    assert newsletter2 is not None  # Should succeed
```

### Integration Tests

1. **Frontend → Backend → Database Flow:**
   - User clicks "Scrape Content" button
   - Verify API returns `total_items > 0`
   - Check database has items with recent `scraped_at`
   - User clicks "Generate Newsletter"
   - Verify newsletter is created successfully

2. **Duplicate Scrape Scenario:**
   - Scrape content from Reddit (110 items)
   - Wait 1 minute
   - Scrape again (same subreddits)
   - Verify: `total_items == 110` (not 0)
   - Generate newsletter
   - Verify: Newsletter created with content

---

## Deployment Checklist

### Pre-Deployment

- [ ] Backup `content_items` table
- [ ] Verify migration 010 has been applied (unique constraint exists)
- [ ] Test fix in development environment
- [ ] Run unit tests
- [ ] Run integration tests

### Deployment Steps

1. **Update Code:**
   ```bash
   # Update save_content_items() method
   # Update load_content_items() method
   git add src/ai_newsletter/database/supabase_client.py
   git commit -m "Fix: Content persistence bug - handle upsert conflicts properly"
   ```

2. **Deploy Backend:**
   ```bash
   # Restart backend server
   # Verify no errors in logs
   ```

3. **Verify Fix:**
   ```bash
   # Test content scraping
   curl -X POST http://localhost:8000/api/v1/content/scrape \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"workspace_id": "$WORKSPACE_ID"}'

   # Check result has total_items > 0

   # Test newsletter generation
   curl -X POST http://localhost:8000/api/v1/newsletters/generate \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"workspace_id": "$WORKSPACE_ID"}'
   ```

### Post-Deployment Monitoring

- [ ] Monitor error logs for upsert failures
- [ ] Check `content_items` table growth
- [ ] Verify newsletter generation success rate increases
- [ ] Monitor database query performance

---

## Prevention Guidelines

### Code Review Checklist

When reviewing database operations:
- ✅ Verify upsert `ignore_duplicates` parameter matches intent
- ✅ Check exception handlers don't swallow errors silently
- ✅ Ensure return values match documented behavior
- ✅ Test duplicate data handling explicitly
- ✅ Verify timestamps are updated on upsert

### Testing Standards

All database operations must include:
1. **Happy path test** - Normal insert
2. **Duplicate test** - Upsert with existing data
3. **Error test** - Constraint violations
4. **Integration test** - End-to-end flow

### Documentation Requirements

All upsert operations must document:
- Which fields are part of the unique constraint
- What happens when duplicates are encountered
- Whether existing records are updated or ignored
- What the return value represents

---

## Related Issues

### Similar Bugs to Check

1. **Other Upsert Operations:**
   - `save_style_profile()` - Line 646
   - `save_workspace_config()` - Line 223
   - Check if they have similar issues

2. **Query Timestamp Dependencies:**
   - All queries using `created_at` filters
   - Consider if they should use `scraped_at` instead
   - Review newsletter, trends, analytics queries

### Future Improvements

1. **Add Upsert Telemetry:**
   - Log: New items inserted
   - Log: Existing items updated
   - Track: Duplicate rate over time

2. **Optimize Duplicate Detection:**
   - Batch check for existing URLs before upsert
   - Skip scraping if content hasn't changed
   - Add content hash to detect actual changes

3. **User Feedback:**
   - Show user: "Updated 50 items, added 60 new items"
   - Distinguish between new and refreshed content
   - Display last scrape time per source

---

## Contact & Questions

For questions about this fix:
1. Review this document
2. Check `docs/SECURITY_FIXES_2025-01-22.md` for related context
3. Review code comments in `supabase_client.py`

**Last Updated:** January 22, 2025
**Status:** FIX IN PROGRESS
**Priority:** CRITICAL
