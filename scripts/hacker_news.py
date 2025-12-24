#!/usr/bin/env python3
"""
Hacker News Scraper for DevOps topics
"""
import requests
import yaml
from datetime import datetime, timedelta
from pathlib import Path
import sys
from typing import List, Dict


def load_config(config_path: str = "data/sources.yml") -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def fetch_hacker_news(keywords: List[str], min_score: int = 50, max_items: int = 10, days_back: int = 1) -> List[Dict]:
    """Fetch relevant Hacker News stories"""
    stories = []
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    try:
        # Use Algolia HN Search API
        base_url = "http://hn.algolia.com/api/v1/search"
        
        for keyword in keywords:
            print(f"Searching Hacker News for '{keyword}'...", file=sys.stderr)
            
            params = {
                'query': keyword,
                'tags': 'story',
                'numericFilters': f'points>={min_score}',
                'hitsPerPage': max_items
            }
            
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            for hit in data.get('hits', []):
                # Parse creation time
                created_at = datetime.fromisoformat(hit['created_at'].replace('Z', '+00:00'))
                
                # Filter by date
                if created_at < cutoff_date:
                    continue
                
                story = {
                    'title': hit.get('title', 'No title'),
                    'url': hit.get('url', f"https://news.ycombinator.com/item?id={hit['objectID']}"),
                    'hn_url': f"https://news.ycombinator.com/item?id={hit['objectID']}",
                    'points': hit.get('points', 0),
                    'author': hit.get('author', 'Unknown'),
                    'num_comments': hit.get('num_comments', 0),
                    'date': created_at.strftime('%Y-%m-%d %H:%M'),
                    'keyword': keyword
                }
                
                # Avoid duplicates
                if not any(s['hn_url'] == story['hn_url'] for s in stories):
                    stories.append(story)
                
    except Exception as e:
        print(f"Error fetching Hacker News: {e}", file=sys.stderr)
    
    return stories


def generate_markdown(stories: List[Dict], title: str) -> str:
    """Generate markdown output for stories"""
    md = f"# {title}\n\n"
    md += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*\n\n"
    
    if not stories:
        md += "No relevant stories found.\n"
        return md
    
    md += f"## Top Stories\n\n"
    
    for story in stories:
        md += f"### [{story['title']}]({story['url']})\n"
        md += f"**Points:** {story['points']} | "
        md += f"**Comments:** {story['num_comments']} | "
        md += f"**Author:** {story['author']} | "
        md += f"**Date:** {story['date']}\n\n"
        md += f"[Discussion on HN]({story['hn_url']})\n\n"
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
    hn_config = config['hacker_news']
    
    # Fetch Hacker News stories
    stories = fetch_hacker_news(
        hn_config['keywords'],
        hn_config['min_score'],
        hn_config['max_items'],
        days_back
    )
    
    # Sort by points (highest first)
    stories.sort(key=lambda x: x['points'], reverse=True)
    
    # Limit results
    stories = stories[:hn_config['max_items']]
    
    # Generate markdown
    title = f"Hacker News DevOps Digest - {report_type.title()}"
    markdown = generate_markdown(stories, title)
    
    # Output to stdout
    print(markdown)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
