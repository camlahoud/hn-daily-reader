# HN Daily Reader

An automatically curated RSS feed of top Hacker News posts, updated daily via GitHub Actions.

## Features

- Fetches yesterday's top HN posts (100+ points) daily at 6:00 AM UTC
- Maintains a rolling 90-day feed
- Accessible via GitHub Pages RSS feed
- No external dependencies (uses Python standard library only)

## Setup

1. **Enable GitHub Pages:**
   - Go to repository Settings > Pages
   - Set Source to "Deploy from a branch"
   - Select `main` branch and `/docs` folder
   - Save

2. **Enable GitHub Actions:**
   - Actions should be enabled by default
   - The workflow runs automatically on the schedule
   - You can also trigger manually via Actions > Update HN Feed > Run workflow

3. **Subscribe to the feed:**
   - Your feed URL will be: `https://YOUR_USERNAME.github.io/hn-daily-reader/feed.xml`
   - Add this URL to your RSS reader

## Configuration

Edit `scripts/fetch_hn_posts.py` to customize:

- `MIN_POINTS`: Minimum points for inclusion (default: 100)
- `POSTS_PER_DAY`: Max posts fetched per day (default: 20)
- `RETENTION_DAYS`: How long to keep posts (default: 90)

Edit `.github/workflows/update-feed.yml` to change the schedule:

```yaml
schedule:
  - cron: '0 6 * * *'  # Runs at 6:00 AM UTC daily
```

## Local Testing

Run the fetch script locally:

```bash
python scripts/fetch_hn_posts.py
```

## How It Works

1. GitHub Actions triggers the workflow daily
2. The Python script fetches yesterday's top posts from the Algolia HN API
3. Posts are merged with existing feed data (duplicates avoided)
4. Posts older than 90 days are pruned
5. RSS feed is regenerated
6. Changes are committed and pushed
7. GitHub Pages serves the updated feed

## License

MIT
