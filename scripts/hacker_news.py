#!/usr/bin/env python3
"""
Hacker News Scraper for DevOps topics
"""
import requests
import yaml
from datetime import datetime, timedelta
import sys
from typing import List, Dict


def load_config(config_path: str = "data/sources.yml") -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def fetch_story_details(story_id: str) -> Dict:
    """Fetch additional details about a story including top comment"""
    try:
        url = f"https://hn.algolia.com/api/v1/items/{story_id}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Get top comment
        top_comment = None
        if data.get('children') and len(data['children']) > 0:
            first_child = data['children'][0]
            if first_child.get('text'):
                # Clean HTML tags from comment
                import re
                comment_text = re.sub('<[^<]+?>', '', first_child['text'])
                top_comment = comment_text[:300] if comment_text else None
        
        return {
            'top_comment': top_comment,
            'num_comments': data.get('children_count', 0)
        }
    except Exception:
        return {'top_comment': None, 'num_comments': 0}


def categorize_story(title: str, url: str) -> List[str]:
    """Categorize story by DevOps topics"""
    categories = []
    text = f"{title} {url}".lower()
    
    category_keywords = {
        'kubernetes': ['kubernetes', 'k8s'],
        'containers': ['docker', 'container', 'podman'],
        'ci/cd': ['ci/cd', 'jenkins', 'gitlab', 'github actions', 'pipeline'],
        'iac': ['terraform', 'ansible', 'pulumi', 'cloudformation'],
        'monitoring': ['monitoring', 'observability', 'prometheus', 'grafana', 'datadog'],
        'cloud': ['aws', 'azure', 'gcp', 'cloud'],
        'gitops': ['gitops', 'argocd', 'flux'],
        'security': ['security', 'devsecops', 'vulnerability']
    }
    
    for category, keywords in category_keywords.items():
        if any(keyword in text for keyword in keywords):
            categories.append(category)
    
    return categories if categories else ['general']


def fetch_hacker_news(
        keywords: List[str],
        min_score: int = 50,
        max_items: int = 10,
        days_back: int = 1) -> List[Dict]:
    """Fetch relevant Hacker News stories"""
    stories = []
    cutoff_date = datetime.now() - timedelta(days=days_back)

    try:
        # Use Algolia HN Search API
        base_url = "https://hn.algolia.com/api/v1/search"

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
                created_at = datetime.fromisoformat(
                    hit['created_at'].replace('Z', '+00:00'))

                # Filter by date
                if created_at < cutoff_date:
                    continue

                # Calculate story age in hours
                age_hours = (datetime.now().replace(tzinfo=created_at.tzinfo) - created_at).total_seconds() / 3600
                
                # Categorize story
                categories = categorize_story(hit.get('title', ''), hit.get('url', ''))
                
                story = {
                    'title': hit.get('title', 'No title'),
                    'url': hit.get(
                        'url',
                        "https://news.ycombinator.com/item?id="
                        f"{hit['objectID']}"
                    ),
                    'hn_url': (
                        "https://news.ycombinator.com/item?id="
                        f"{hit['objectID']}"
                    ),
                    'points': hit.get('points', 0),
                    'author': hit.get('author', 'Unknown'),
                    'num_comments': hit.get('num_comments', 0),
                    'date': created_at.strftime('%Y-%m-%d %H:%M'),
                    'keyword': keyword,
                    'age_hours': int(age_hours),
                    'categories': categories,
                    'objectID': hit['objectID']
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

    # Add summary statistics
    md += f"💬 **Total Stories:** {len(stories)} | "
    total_points = sum(s['points'] for s in stories)
    total_comments = sum(s['num_comments'] for s in stories)
    md += f"**Total Points:** {total_points} | **Total Comments:** {total_comments}\n\n"
    
    # Categorize stories
    all_categories = {}
    for story in stories:
        for category in story.get('categories', ['general']):
            all_categories[category] = all_categories.get(category, 0) + 1
    
    if all_categories:
        md += "📂 **Topics:** "
        md += " | ".join([f"{cat.title()} ({count})" for cat, count in sorted(all_categories.items(), key=lambda x: x[1], reverse=True)])
        md += "\n\n"
    
    md += "---\n\n"
    
    # Group stories by category
    by_category = {}
    for story in stories:
        for category in story.get('categories', ['general']):
            if category not in by_category:
                by_category[category] = []
            if story not in by_category[category]:
                by_category[category].append(story)

    # Generate markdown by category
    for category in sorted(by_category.keys()):
        items = by_category[category]
        md += f"## {category.upper()}\n\n"
        md += f"*{len(items)} story/stories*\n\n"
        
        for story in items:
            md += f"### [{story['title']}]({story['url']})\n\n"
            
            # Metrics bar
            md += f"👤 **Author:** {story['author']} | "
            md += f"⬆️ **Points:** {story['points']} | "
            md += f"💬 **Comments:** {story['num_comments']} | "
            md += f"📅 **Date:** {story['date']}"
            
            # Add trending indicator for recent popular stories
            if story['age_hours'] < 24 and story['points'] > 100:
                md += " | 🔥 **Trending**"
            
            md += "\n\n"
            
            # Categories
            if len(story.get('categories', [])) > 1:
                other_cats = [c for c in story['categories'] if c != category]
                if other_cats:
                    md += f"🏷️ Also in: {', '.join(other_cats)}\n\n"
            
            md += f"[Discussion on Hacker News]({story['hn_url']})\n\n"
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
