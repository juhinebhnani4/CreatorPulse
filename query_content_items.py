import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "backend"))

from backend.database import get_supabase_service_client
from datetime import datetime, timezone

db = get_supabase_service_client()

# Get workspace ID
workspaces = db.table('workspaces').select('id, name').limit(1).execute()
workspace_id = workspaces.data[0]['id']

print(f"Workspace: {workspace_id}\n")

# Get all content items
result = db.table('content_items') \
    .select('id, title, source, scraped_at, created_at, score') \
    .eq('workspace_id', workspace_id) \
    .order('scraped_at', desc=True) \
    .limit(50) \
    .execute()

now = datetime.now(timezone.utc)
print(f"Current time (UTC): {now}\n")
print(f"Total items: {len(result.data)}\n")

age_buckets = {
    '0-3 days': 0,
    '4-7 days': 0,
    '8-14 days': 0,
    '15-30 days': 0,
    '30+ days': 0
}

for item in result.data:
    scraped_at = datetime.fromisoformat(item['scraped_at'].replace('Z', '+00:00'))
    age_days = (now - scraped_at).days
    
    print(f"ID: {item['id'][:8]}... | Source: {item['source']:8s} | Age: {age_days:4d} days | Score: {item.get('score', 0):5s} | Title: {item['title'][:60]}")
    
    if age_days <= 3:
        age_buckets['0-3 days'] += 1
    elif age_days <= 7:
        age_buckets['4-7 days'] += 1
    elif age_days <= 14:
        age_buckets['8-14 days'] += 1
    elif age_days <= 30:
        age_buckets['15-30 days'] += 1
    else:
        age_buckets['30+ days'] += 1

print("\n" + "="*80)
print("AGE DISTRIBUTION:")
for bucket, count in age_buckets.items():
    pct = (count / len(result.data) * 100) if result.data else 0
    print(f"  {bucket:12s}: {count:3d} items ({pct:5.1f}%)")
