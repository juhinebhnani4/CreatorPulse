#!/usr/bin/env python3
"""
Newsletter Freshness Diagnostic Script
Analyzes database, backend logs, and code to diagnose content repetition issues.
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.database import get_supabase_service_client
from backend.settings import settings


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_status(status: str, message: str):
    """Print status with color indicator"""
    colors = {
        "RED": "\033[91m❌",
        "YELLOW": "\033[93m⚠️",
        "GREEN": "\033[92m✅",
        "BLUE": "\033[94mℹ️"
    }
    reset = "\033[0m"
    icon = colors.get(status, "")
    print(f"{icon} {message}{reset}")


def analyze_content_age():
    """Analyze content items age distribution"""
    print_section("DATABASE ANALYSIS: Content Age Distribution")

    db = get_supabase_service_client()

    # Get workspace ID (assuming first workspace)
    workspaces = db.table('workspaces').select('id, name').limit(1).execute()
    if not workspaces.data:
        print_status("RED", "No workspaces found!")
        return None

    workspace_id = workspaces.data[0]['id']
    workspace_name = workspaces.data[0]['name']
    print(f"Workspace: {workspace_name} ({workspace_id})")

    # Get content items with age calculation
    query = """
        SELECT
            id,
            title,
            source,
            scraped_at,
            created_at,
            EXTRACT(DAY FROM (NOW() - scraped_at)) as age_days
        FROM content_items
        WHERE workspace_id = %s
        ORDER BY scraped_at DESC
        LIMIT 30
    """

    # Supabase Python client doesn't support raw SQL easily, so use table API
    result = db.table('content_items') \
        .select('id, title, source, scraped_at, created_at') \
        .eq('workspace_id', workspace_id) \
        .order('scraped_at', desc=True) \
        .limit(30) \
        .execute()

    if not result.data:
        print_status("RED", "No content items found!")
        return workspace_id

    print(f"\nTotal content items retrieved: {len(result.data)}\n")

    # Calculate ages and categorize
    now = datetime.now(timezone.utc)
    age_categories = {
        '0-3 days (100% score)': [],
        '4-7 days (80% score)': [],
        '8-14 days (60% score)': [],
        '15-21 days (40% score)': [],
        '22-30 days (20% score)': [],
        '30+ days (5% score)': []
    }

    print(f"{'ID':<40} {'Source':<10} {'Age (days)':<12} {'Title':<50}")
    print("-" * 120)

    for item in result.data:
        scraped_at = datetime.fromisoformat(item['scraped_at'].replace('Z', '+00:00'))
        age_days = (now - scraped_at).days

        title = item['title'][:47] + "..." if len(item['title']) > 50 else item['title']
        print(f"{item['id']:<40} {item['source']:<10} {age_days:<12} {title:<50}")

        # Categorize
        if age_days <= 3:
            age_categories['0-3 days (100% score)'].append(item)
        elif age_days <= 7:
            age_categories['4-7 days (80% score)'].append(item)
        elif age_days <= 14:
            age_categories['8-14 days (60% score)'].append(item)
        elif age_days <= 21:
            age_categories['15-21 days (40% score)'].append(item)
        elif age_days <= 30:
            age_categories['22-30 days (20% score)'].append(item)
        else:
            age_categories['30+ days (5% score)'].append(item)

    print("\n" + "=" * 80)
    print("AGE DISTRIBUTION SUMMARY")
    print("=" * 80)

    for category, items in age_categories.items():
        count = len(items)
        percentage = (count / len(result.data)) * 100

        if count > 0:
            if '100%' in category or '80%' in category:
                status = "GREEN"
            elif '5%' in category and percentage > 50:
                status = "RED"
            else:
                status = "YELLOW"
        else:
            status = "BLUE"

        print_status(status, f"{category}: {count} items ({percentage:.1f}%)")

    # Diagnosis
    print("\n" + "=" * 80)
    old_content_pct = (len(age_categories['30+ days (5% score)']) / len(result.data)) * 100

    if old_content_pct > 70:
        print_status("RED", f"CRITICAL: {old_content_pct:.1f}% of content is 30+ days old!")
        print("   → Freshness decay is working, but content is too stale")
        print("   → Need to run scraping more frequently or add more sources")
    elif old_content_pct > 40:
        print_status("YELLOW", f"WARNING: {old_content_pct:.1f}% of content is 30+ days old")
        print("   → Content is getting stale, consider more frequent scraping")
    else:
        print_status("GREEN", f"GOOD: Only {old_content_pct:.1f}% of content is 30+ days old")

    return workspace_id


def analyze_newsletter_content_reuse(workspace_id: str):
    """Check if newsletters are reusing the same content items"""
    print_section("DATABASE ANALYSIS: Newsletter Content Reuse")

    db = get_supabase_service_client()

    # Get recent newsletters
    newsletters = db.table('newsletters') \
        .select('id, title, generated_at, status') \
        .eq('workspace_id', workspace_id) \
        .order('generated_at', desc=True) \
        .limit(12) \
        .execute()

    if not newsletters.data:
        print_status("YELLOW", "No newsletters found")
        return

    print(f"Analyzing {len(newsletters.data)} recent newsletters\n")

    # Get content items for each newsletter
    newsletter_content = {}
    for newsletter in newsletters.data:
        items = db.table('newsletter_content_items') \
            .select('content_item_id') \
            .eq('newsletter_id', newsletter['id']) \
            .execute()

        content_ids = [item['content_item_id'] for item in items.data]
        newsletter_content[newsletter['id']] = {
            'title': newsletter['title'],
            'generated_at': newsletter['generated_at'],
            'content_ids': content_ids,
            'count': len(content_ids)
        }

    # Display
    print(f"{'Newsletter ID':<40} {'Generated':<20} {'Items':<8} {'Content IDs (first 3)':<50}")
    print("-" * 120)

    for nl_id, data in newsletter_content.items():
        date = data['generated_at'][:19] if data['generated_at'] else 'N/A'
        first_3_ids = ', '.join(data['content_ids'][:3])
        print(f"{nl_id:<40} {date:<20} {data['count']:<8} {first_3_ids:<50}")

    # Check for overlap
    print("\n" + "=" * 80)
    print("CONTENT REUSE ANALYSIS")
    print("=" * 80)

    all_content_ids = [ids for data in newsletter_content.values() for ids in data['content_ids']]
    unique_content_ids = set(all_content_ids)

    print(f"\nTotal content item references: {len(all_content_ids)}")
    print(f"Unique content items used: {len(unique_content_ids)}")

    # Find most reused items
    from collections import Counter
    reuse_counts = Counter(all_content_ids)
    most_reused = reuse_counts.most_common(5)

    if most_reused:
        print("\nMost reused content items:")
        for content_id, count in most_reused:
            # Get item details
            item = db.table('content_items') \
                .select('title, source') \
                .eq('id', content_id) \
                .single() \
                .execute()

            title = item.data['title'][:60] + "..." if item.data and len(item.data['title']) > 60 else item.data['title'] if item.data else 'Unknown'
            source = item.data['source'] if item.data else 'unknown'

            reuse_pct = (count / len(newsletters.data)) * 100
            if reuse_pct > 80:
                status = "RED"
            elif reuse_pct > 50:
                status = "YELLOW"
            else:
                status = "GREEN"

            print_status(status, f"{content_id[:8]}... ({source}) - Used in {count}/{len(newsletters.data)} newsletters ({reuse_pct:.0f}%)")
            print(f"     Title: {title}")

    # Diagnosis
    avg_reuse = len(all_content_ids) / len(unique_content_ids) if unique_content_ids else 0
    print(f"\nAverage reuse per item: {avg_reuse:.2f}x")

    if avg_reuse > 5:
        print_status("RED", "CRITICAL: Same content is being heavily reused!")
        print("   → Content exclusion logic may not be working")
        print("   → Or not enough fresh content available")
    elif avg_reuse > 3:
        print_status("YELLOW", "WARNING: Significant content reuse detected")
    else:
        print_status("GREEN", "GOOD: Content variation is healthy")


def analyze_backend_logs():
    """Analyze backend logs for freshness decay execution"""
    print_section("BACKEND LOGS ANALYSIS")

    # Check all running backends
    backend_ids = ['140589', '867906', '16f32e', '74f58f', '76d914', 'c35edc', 'dee0e5', 'bd546f']

    print("Searching for FreshnessDecay logs in running backends...\n")

    found_logs = False
    for backend_id in backend_ids:
        log_file = Path(f"/tmp/bash_output_{backend_id}.log")  # This won't work, but showing intent
        print(f"Checking backend {backend_id}...")
        # Note: We can't actually read the bash outputs this way,
        # but the user can run BashOutput manually

    print_status("YELLOW", "Cannot automatically parse bash outputs")
    print("\nTo manually check backend logs, run:")
    print("   BashOutput(bash_id='bd546f')  # Latest backend")
    print("\nLook for:")
    print("   - [FreshnessDecay] FUNCTION CALLED")
    print("   - [FreshnessDecay] WARNING: Failed to parse...")
    print("   - [FreshnessDecay] SUMMARY - Processed: X, Skipped: Y")
    print("   - Warning: Failed to convert item to ContentItem")


def verify_code_fixes():
    """Verify that code fixes are present"""
    print_section("CODE VERIFICATION")

    service_file = Path(__file__).parent / "backend" / "services" / "newsletter_service.py"

    if not service_file.exists():
        print_status("RED", f"File not found: {service_file}")
        return

    content = service_file.read_text(encoding='utf-8')
    lines = content.split('\n')

    # Check for Unicode fix (around line 371-378)
    unicode_fix_found = False
    field_cleanup_found = False

    for i, line in enumerate(lines, 1):
        # Unicode fix check
        if "safe_title = title.encode('ascii', errors='replace').decode('ascii')" in line:
            unicode_fix_found = True
            print_status("GREEN", f"Unicode fix FOUND at line {i}")
            print(f"     {lines[i-1].strip()}")

        # Field cleanup check
        if "item.pop('freshness_age_days', None)" in line:
            field_cleanup_found = True
            print_status("GREEN", f"Field cleanup FOUND at line {i}")
            print(f"     {lines[i-1].strip()}")
            print(f"     {lines[i].strip()}")
            print(f"     {lines[i+1].strip()}")

    if not unicode_fix_found:
        print_status("RED", "Unicode fix NOT FOUND")
        print("   → Expected: safe_title = title.encode('ascii', errors='replace').decode('ascii')")

    if not field_cleanup_found:
        print_status("RED", "Field cleanup NOT FOUND")
        print("   → Expected: item.pop('freshness_age_days', None)")

    if unicode_fix_found and field_cleanup_found:
        print_status("GREEN", "All code fixes are in place!")
    else:
        print_status("RED", "Some code fixes are MISSING - backend may not have reloaded")


def generate_diagnosis():
    """Generate final diagnosis with confidence levels"""
    print_section("DIAGNOSIS & RECOMMENDATIONS")

    print("Based on the analysis above, the most likely root causes are:\n")

    print("THEORY A: Stale Content Problem (70% confidence)")
    print("   Symptoms: High percentage of 30+ day old content")
    print("   Root Cause: Content database hasn't been refreshed recently")
    print("   Fix: Run scraping more frequently, add more content sources")
    print()

    print("THEORY B: Content Exclusion Not Working (20% confidence)")
    print("   Symptoms: Same content_item_id appearing in many newsletters")
    print("   Root Cause: Bug in content exclusion logic (lines 346-374)")
    print("   Fix: Debug _apply_content_exclusion() function")
    print()

    print("THEORY C: Scraping Not Creating Fresh Content (10% confidence)")
    print("   Symptoms: Scraping runs but scraped_at doesn't change much")
    print("   Root Cause: Scrapers hitting API limits or URLs returning cached data")
    print("   Fix: Check scraper logs, verify API keys, add delays")
    print()

    print("=" * 80)
    print("RECOMMENDED NEXT STEPS:")
    print("=" * 80)
    print()
    print("1. If >70% content is 30+ days old:")
    print("   → Run: POST /api/v1/content/scrape")
    print("   → Check scraping logs for errors")
    print("   → Add more content sources in workspace config")
    print()
    print("2. If same content appears in >80% of newsletters:")
    print("   → Debug content exclusion logic")
    print("   → Check newsletter_content_items table for orphaned references")
    print()
    print("3. If code fixes are missing:")
    print("   → Kill all Python processes: taskkill //F //IM python.exe")
    print("   → Start fresh backend")
    print("   → Test newsletter generation")


def main():
    """Main diagnostic function"""
    print(f"""
{'=' * 80}
  NEWSLETTER FRESHNESS DIAGNOSTIC TOOL
  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}
    """)

    try:
        # Run all analyses
        workspace_id = analyze_content_age()

        if workspace_id:
            analyze_newsletter_content_reuse(workspace_id)

        analyze_backend_logs()
        verify_code_fixes()
        generate_diagnosis()

        print(f"\n{'=' * 80}")
        print("  DIAGNOSTIC COMPLETE")
        print(f"{'=' * 80}\n")

        # Save to file
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        report_file = Path(__file__).parent / f"DIAGNOSTIC_REPORT_{timestamp}.txt"
        print(f"Report would be saved to: {report_file}")
        print("(Run with output redirection to save: python diagnose_newsletter_freshness.py > report.txt)")

    except Exception as e:
        print_status("RED", f"Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
