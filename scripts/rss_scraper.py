#!/usr/bin/env python3
"""
RSS Feed Scraper for DevOps sources
"""
import feedparser
import yaml
from datetime import datetime, timedelta
import sys
from typing import List, Dict
import re


def load_config(config_path: str = "data/sources.yml") -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def clean_html(text: str) -> str:
    """Remove HTML tags from text"""
    if not text:
        return ""
    # Remove HTML tags
    clean = re.sub('<[^<]+?>', '', text)
    # Remove extra whitespace
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()


def extract_tags(text: str) -> List[str]:
    """Extract relevant DevOps keywords/tags from text"""
    devops_keywords = [
        'kubernetes', 'docker', 'terraform', 'ansible', 'jenkins',
        'gitlab', 'github', 'ci/cd', 'devops', 'cloud', 'aws', 'azure',
        'gcp', 'monitoring', 'observability', 'prometheus', 'grafana',
        'gitops', 'argocd', 'helm', 'containerization', 'microservices',
        'infrastructure', 'automation', 'deployment', 'pipeline',
        'security', 'devsecops', 'sre', 'reliability'
    ]
    
    text_lower = text.lower()
    found_tags = [keyword for keyword in devops_keywords if keyword in text_lower]
    return list(set(found_tags))[:5]  # Return up to 5 unique tags


def estimate_reading_time(text: str) -> int:
    """Estimate reading time in minutes (avg 200 words/min)"""
    word_count = len(text.split())
    return max(1, round(word_count / 200))


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

                # Get full content or summary
                if 'content' in entry and entry.content:
                    content = entry.content[0].get('value', '')
                else:
                    content = entry.get('summary', '')
                
                # Clean HTML from content
                content = clean_html(content)
                summary_text = content[:500] if content else ''
                if len(content) > 500:
                    summary_text += '...'
                
                # Extract author
                author = entry.get('author', '')
                if not author and 'authors' in entry and entry.authors:
                    author = entry.authors[0].get('name', '')
                
                # Extract tags
                full_text = f"{entry.get('title', '')} {content}"
                tags = extract_tags(full_text)
                
                article = {
                    'title': entry.get('title', 'No title'),
                    'link': entry.get('link', ''),
                    'source': feed_config['name'],
                    'category': feed_config['category'],
                    'date': pub_date.strftime(
                        '%Y-%m-%d %H:%M') if pub_date else 'Unknown',
                    'date_obj': pub_date if pub_date else datetime.min,
                    'summary': summary_text,
                    'author': author,
                    'tags': tags,
                    'reading_time': estimate_reading_time(content)
                }
                articles.append(article)

        except Exception as e:
            print(f"Error fetching {feed_config['name']}: {e}",
                  file=sys.stderr)

    return articles


def generate_markdown(articles: List[Dict], title: str) -> str:
    """Generate markdown output for articles"""
    md = f"# {title}\n\n"
    md += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*\n\n"

    if not articles:
        md += "No new articles found.\n"
        return md

    # Add summary statistics
    md += f"📊 **Total Articles:** {len(articles)} | "
    categories = set(article['category'] for article in articles)
    md += f"**Categories:** {len(categories)}\n\n"
    
    # Add top tags section
    all_tags = {}
    for article in articles:
        for tag in article.get('tags', []):
            all_tags[tag] = all_tags.get(tag, 0) + 1
    
    if all_tags:
        top_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:8]
        md += "🏷️ **Trending Topics:** "
        md += " | ".join([f"{tag} ({count})" for tag, count in top_tags])
        md += "\n\n---\n\n"

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
        md += f"*{len(items)} article(s)*\n\n"
        
        for item in items:
            md += f"### [{item['title']}]({item['link']})\n\n"
            
            # Metadata line
            metadata_parts = [f"**Source:** {item['source']}"]
            if item.get('author'):
                metadata_parts.append(f"**Author:** {item['author']}")
            metadata_parts.append(f"**Date:** {item['date']}")
            if item.get('reading_time', 0) > 0:
                metadata_parts.append(f"**Reading Time:** ~{item['reading_time']} min")
            md += " | ".join(metadata_parts) + "\n\n"
            
            # Tags
            if item.get('tags'):
                md += f"🏷️ {', '.join(item['tags'])}\n\n"
            
            # Summary
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
    articles.sort(key=lambda x: x['date_obj'], reverse=True)

    # Generate markdown
    title = f"DevOps RSS Feed Digest - {report_type.title()}"
    markdown = generate_markdown(articles, title)

    # Output to stdout
    print(markdown)

    return 0


if __name__ == "__main__":
    sys.exit(main())
