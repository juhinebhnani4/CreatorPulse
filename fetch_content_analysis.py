#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "backend"))

from backend.database import get_supabase_service_client
from datetime import datetime, timezone
from collections import defaultdict

print("=" * 100)
print("CONTENT ITEMS ANALYSIS - FETCHING FROM SUPABASE")
print("=" * 100)

db = get_supabase_service_client()

# Get workspace
workspaces = db.table('workspaces').select('id, name').limit(1).execute()
if not workspaces.data:
    print("ERROR: No workspace found!")
    sys.exit(1)

workspace_id = workspaces.data[0]['id']
workspace_name = workspaces.data[0]['name']

print(f"\nWorkspace: {workspace_name}")
print(f"Workspace ID: {workspace_id}")

# Fetch ALL content items
result = db.table('content_items') \
    .select('id, title, source, scraped_at, created_at, score') \
    .eq('workspace_id', workspace_id) \
    .order('scraped_at', desc=True) \
    .execute()

now = datetime.now(timezone.utc)
print(f"\nCurrent UTC Time: {now}")
print(f"Total Content Items: {len(result.data)}")

# Analysis buckets
age_buckets = defaultdict(int)
source_counts = defaultdict(int)
source_ages = defaultdict(list)

print("\n" + "=" * 100)
print("DETAILED CONTENT LIST (Most Recent First)")
print("=" * 100)
print(f"{'ID':<10} {'Source':<10} {'Age (days)':<12} {'Score':<8} {'Scraped At':<20} {'Title':<40}")
print("-" * 100)

for item in result.data:
    try:
        scraped_at_str = item['scraped_at'].replace('Z', '+00:00')
        scraped_at = datetime.fromisoformat(scraped_at_str)
        age_days = (now - scraped_at).days
        
        source = item['source']
        score = item.get('score') or 0
        title = (item['title'][:37] + "...") if len(item['title']) > 40 else item['title']
        
        # Collect stats
        source_counts[source] += 1
        source_ages[source].append(age_days)
        
        # Categorize age
        if age_days < 0:
            age_buckets['FUTURE (ERROR)'] += 1
        elif age_days <= 3:
            age_buckets['0-3 days (Fresh)'] += 1
        elif age_days <= 7:
            age_buckets['4-7 days'] += 1
        elif age_days <= 14:
            age_buckets['8-14 days'] += 1
        elif age_days <= 30:
            age_buckets['15-30 days'] += 1
        else:
            age_buckets['30+ days (Stale)'] += 1
        
        print(f"{item['id'][:8]:<10} {source:<10} {age_days:<12} {score:<8} {scraped_at_str[:19]:<20} {title:<40}")
        
    except Exception as e:
        print(f"ERROR parsing item {item['id']}: {e}")

# Print age distribution
print("\n" + "=" * 100)
print("AGE DISTRIBUTION")
print("=" * 100)
total = len(result.data)
for bucket in ['0-3 days (Fresh)', '4-7 days', '8-14 days', '15-30 days', '30+ days (Stale)', 'FUTURE (ERROR)']:
    count = age_buckets[bucket]
    if count > 0:
        pct = (count / total * 100)
        bar = "#" * int(pct / 2)
        print(f"{bucket:<25}: {count:3d} items ({pct:5.1f}%) {bar}")

# Print source breakdown
print("\n" + "=" * 100)
print("SOURCE BREAKDOWN")
print("=" * 100)
print(f"{'Source':<15} {'Count':<8} {'Avg Age':<12} {'Min Age':<10} {'Max Age':<10}")
print("-" * 100)
for source in sorted(source_counts.keys()):
    count = source_counts[source]
    ages = source_ages[source]
    avg_age = sum(ages) / len(ages)
    min_age = min(ages)
    max_age = max(ages)
    print(f"{source:<15} {count:<8} {avg_age:>10.1f}d {min_age:>8d}d {max_age:>8d}d")

# Find the most recent content
print("\n" + "=" * 100)
print("MOST RECENT CONTENT (TOP 10)")
print("=" * 100)
sorted_items = sorted(result.data, key=lambda x: x['scraped_at'], reverse=True)
for i, item in enumerate(sorted_items[:10], 1):
    scraped_at = datetime.fromisoformat(item['scraped_at'].replace('Z', '+00:00'))
    age_days = (now - scraped_at).days
    title = (item['title'][:50] + "...") if len(item['title']) > 50 else item['title']
    print(f"{i:2d}. [{item['source']:8s}] {age_days:3d}d ago - {title}")

print("\n" + "=" * 100)
