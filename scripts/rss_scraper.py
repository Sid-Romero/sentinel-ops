#!/usr/bin/env python3
"""
RSS Feed Scraper for DevOps sources
"""
import feedparser
import yaml
from datetime import datetime, timedelta
import sys
from typing import List, Dict


def load_config(config_path: str = "data/sources.yml") -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def fetch_rss_feeds(feeds: List[Dict], days_back: int = 1) -> List[Dict]:
    """Fetch and parse RSS feeds"""
    articles = []
    cutoff_date = datetime.now() - timedelta(days=days_back)

    for feed_config in feeds:
        try:
            print(f"Fetching {feed_config['name']}...", file=sys.stderr)
            feed = feedparser.parse(feed_config['url'])

            for entry in feed.entries[:10]:  # Limit to 10 most recent
                # Parse publication date
                pub_date = None
                if hasattr(
                        entry,
                        'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])

                # Filter by date
                if pub_date and pub_date < cutoff_date:
                    continue

                article = {
                    'title': entry.get('title', 'No title'),
                    'link': entry.get('link', ''),
                    'source': feed_config['name'],
                    'category': feed_config['category'],
                    'date': pub_date.strftime(
                        '%Y-%m-%d %H:%M') if pub_date else 'Unknown',
                    'summary': entry.get('summary', '')[:200] + '...'
                    if entry.get('summary') else ''
                }
                articles.append(article)

        except Exception as e:
            print(
                f"Error fetching {
                    feed_config['name']}: {e}",
                file=sys.stderr)

    return articles


def generate_markdown(articles: List[Dict], title: str) -> str:
    """Generate markdown output for articles"""
    md = f"# {title}\n\n"
    md += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*\n\n"

    if not articles:
        md += "No new articles found.\n"
        return md

    # Group by category
    by_category = {}
    for article in articles:
        category = article['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(article)

    # Generate markdown by category
    for category, items in sorted(by_category.items()):
        md += f"## {category.title()}\n\n"
        for item in items:
            md += f"### [{item['title']}]({item['link']})\n"
            md += f"**Source:** {item['source']} | **Date:** {item['date']}\n\n"
            if item['summary']:
                md += f"{item['summary']}\n\n"
            md += "---\n\n"

    return md


def main():
    """Main execution function"""
    # Determine if daily or weekly
    days_back = 1
    report_type = "daily"

    if len(sys.argv) > 1 and sys.argv[1] == "--weekly":
        days_back = 7
        report_type = "weekly"

    # Load configuration
    config = load_config()

    # Fetch RSS feeds
    articles = fetch_rss_feeds(config['rss_feeds'], days_back)

    # Sort by date (newest first)
    articles.sort(key=lambda x: x['date'], reverse=True)

    # Generate markdown
    title = f"DevOps RSS Feed Digest - {report_type.title()}"
    markdown = generate_markdown(articles, title)

    # Output to stdout
    print(markdown)

    return 0


if __name__ == "__main__":
    sys.exit(main())
