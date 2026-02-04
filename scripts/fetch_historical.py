#!/usr/bin/env python3
"""
Ad-hoc script to fetch HN posts from N days ago.
Useful for backfilling the feed or working around RSS reader quirks.

Usage:
    python scripts/fetch_historical.py          # Defaults to 2 days ago
    python scripts/fetch_historical.py 3        # Fetch from 3 days ago
    python scripts/fetch_historical.py 2 5      # Fetch from 2 to 5 days ago (inclusive)
"""

import sys
from datetime import datetime, timedelta, timezone

# Import functions from the main script
from fetch_hn_posts import (
    FEED_DATA_FILE,
    RSS_FILE,
    MIN_POINTS,
    fetch_hn_posts,
    load_feed_data,
    save_feed_data,
    prune_old_posts,
    generate_rss,
)


def get_day_timestamps(days_ago):
    """Get Unix timestamps for a specific day N days ago (UTC)."""
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    day_start = today - timedelta(days=days_ago)
    day_end = day_start + timedelta(days=1) - timedelta(seconds=1)
    return int(day_start.timestamp()), int(day_end.timestamp())


def main():
    # Parse arguments
    if len(sys.argv) == 1:
        # Default: 2 days ago only
        start_days = end_days = 2
    elif len(sys.argv) == 2:
        # Single day
        start_days = end_days = int(sys.argv[1])
    else:
        # Range: from start_days to end_days ago
        start_days = int(sys.argv[1])
        end_days = int(sys.argv[2])

    if start_days > end_days:
        start_days, end_days = end_days, start_days

    print("=" * 60)
    print("HN Daily Reader - Fetching historical posts")
    print("=" * 60)

    # Load existing feed data
    feed_data = load_feed_data(FEED_DATA_FILE)
    existing_ids = {p["id"] for p in feed_data["posts"]}
    print(f"Existing feed has {len(feed_data['posts'])} posts")

    total_added = 0

    # Fetch posts for each day in the range
    for days_ago in range(start_days, end_days + 1):
        start_ts, end_ts = get_day_timestamps(days_ago)
        target_date = datetime.fromtimestamp(start_ts, tz=timezone.utc)
        print(f"\nFetching posts from: {target_date.strftime('%Y-%m-%d')} ({days_ago} days ago)")

        # Fetch posts for this day
        new_posts = fetch_hn_posts(start_ts, end_ts)
        print(f"Found {len(new_posts)} posts with >= {MIN_POINTS} points")

        # Add new posts (avoid duplicates)
        added = 0
        for post in new_posts:
            if post["id"] not in existing_ids:
                feed_data["posts"].append(post)
                existing_ids.add(post["id"])
                added += 1
                print(f"  + [{post['points']} pts] {post['title'][:50]}...")

        print(f"Added {added} new posts from {target_date.strftime('%Y-%m-%d')}")
        total_added += added

    # Prune old posts
    original_count = len(feed_data["posts"])
    feed_data["posts"] = prune_old_posts(feed_data["posts"])
    pruned = original_count - len(feed_data["posts"])
    if pruned > 0:
        print(f"\nPruned {pruned} posts older than retention period")

    # Update metadata
    feed_data["last_updated"] = datetime.now(timezone.utc).isoformat()

    # Save feed data
    save_feed_data(FEED_DATA_FILE, feed_data)
    print(f"\nSaved feed data to {FEED_DATA_FILE}")

    # Generate RSS
    generate_rss(feed_data["posts"], RSS_FILE)
    print(f"Generated RSS feed at {RSS_FILE}")

    print("\n" + "=" * 60)
    print(f"Total added: {total_added} posts")
    print(f"Feed now contains {len(feed_data['posts'])} posts")
    print("Done!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
