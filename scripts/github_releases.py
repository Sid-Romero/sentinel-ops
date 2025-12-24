#!/usr/bin/env python3
"""
GitHub Releases Monitor for DevOps tools
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


def extract_changelog_highlights(body: str) -> Dict[str, List[str]]:
    """Extract key sections from release notes"""
    highlights = {
        'breaking': [],
        'features': [],
        'fixes': [],
        'security': []
    }
    
    if not body:
        return highlights
    
    body_lower = body.lower()
    lines = body.split('\n')
    
    # Look for breaking changes
    breaking_keywords = ['breaking', 'breaking change', 'breaking changes', '⚠️', '🚨']
    for line in lines[:30]:  # Check first 30 lines
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in breaking_keywords):
            highlights['breaking'].append(line.strip('*- #'))
    
    # Look for security updates
    security_keywords = ['security', 'vulnerability', 'cve', 'patch']
    for line in lines[:30]:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in security_keywords):
            highlights['security'].append(line.strip('*- #'))
    
    # Look for new features (basic detection)
    feature_keywords = ['feature', 'add', 'new', '✨', '🎉']
    for line in lines[:20]:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in feature_keywords) and len(line) > 10:
            if line not in highlights['breaking'] and line not in highlights['security']:
                highlights['features'].append(line.strip('*- #'))
    
    # Look for fixes
    fix_keywords = ['fix', 'bug', 'resolve', '🐛']
    for line in lines[:20]:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in fix_keywords) and len(line) > 10:
            if line not in highlights['breaking'] and line not in highlights['security'] and line not in highlights['features']:
                highlights['fixes'].append(line.strip('*- #'))
    
    # Limit each section
    for key in highlights:
        highlights[key] = highlights[key][:3]
    
    return highlights


def fetch_github_releases(repos: List[Dict], days_back: int = 1) -> List[Dict]:
    """Fetch latest releases from GitHub repositories"""
    releases = []
    cutoff_date = datetime.now() - timedelta(days=days_back)

    headers = {
        'Accept': 'application/vnd.github.v3+json',
    }

    # Add GitHub token if available (for higher rate limits)
    import os
    github_token = os.environ.get('GITHUB_TOKEN')
    if github_token:
        headers['Authorization'] = f'token {github_token}'

    for repo_config in repos:
        try:
            repo = repo_config['repo']
            print(f"Fetching releases for {repo}...", file=sys.stderr)

            url = f"https://api.github.com/repos/{repo}/releases"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            repo_releases = response.json()

            for release in repo_releases[:5]:  # Limit to 5 most recent
                # Parse publication date
                published_at = datetime.strptime(
                    release['published_at'],
                    '%Y-%m-%dT%H:%M:%SZ'
                )

                # Filter by date
                if published_at < cutoff_date:
                    continue

                body = release.get('body', '')
                body_preview = body[:600] if body else ''
                if len(body) > 600:
                    body_preview += '...'
                
                # Extract highlights
                highlights = extract_changelog_highlights(body)
                
                release_info = {
                    'name': repo_config['name'],
                    'repo': repo,
                    'version': release.get('tag_name', 'Unknown'),
                    'title': release.get(
                        'name', release.get('tag_name', 'No title')),
                    'url': release.get('html_url', ''),
                    'date': published_at.strftime('%Y-%m-%d %H:%M'),
                    'date_obj': published_at,
                    'category': repo_config['category'],
                    'prerelease': release.get('prerelease', False),
                    'body': body_preview,
                    'highlights': highlights,
                    'assets_count': len(release.get('assets', []))
                }
                releases.append(release_info)

        except Exception as e:
            print(f"Error fetching {repo_config['repo']}: {e}",
                  file=sys.stderr)

    return releases


def generate_markdown(releases: List[Dict], title: str) -> str:
    """Generate markdown output for releases"""
    md = f"# {title}\n\n"
    md += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*\n\n"

    if not releases:
        md += "No new releases found.\n"
        return md

    # Add summary statistics
    md += f"📦 **Total Releases:** {len(releases)} | "
    categories = set(release['category'] for release in releases)
    md += f"**Categories:** {len(categories)}\n\n"
    
    # Count pre-releases and breaking changes
    prerelease_count = sum(1 for r in releases if r.get('prerelease'))
    breaking_count = sum(1 for r in releases if r.get('highlights', {}).get('breaking'))
    security_count = sum(1 for r in releases if r.get('highlights', {}).get('security'))
    
    indicators = []
    if prerelease_count > 0:
        indicators.append(f"⚠️ {prerelease_count} pre-release(s)")
    if breaking_count > 0:
        indicators.append(f"🚨 {breaking_count} with breaking changes")
    if security_count > 0:
        indicators.append(f"🔒 {security_count} with security updates")
    
    if indicators:
        md += " | ".join(indicators) + "\n\n"
    
    md += "---\n\n"

    # Group by category
    by_category = {}
    for release in releases:
        category = release['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(release)

    # Generate markdown by category
    for category, items in sorted(by_category.items()):
        md += f"## {category.title()}\n\n"
        md += f"*{len(items)} release(s)*\n\n"
        
        for item in items:
            prerelease_tag = " ⚠️ (Pre-release)" if item['prerelease'] else ""
            md += f"### {item['name']} {item['version']}{prerelease_tag}\n\n"
            
            # Metadata
            md += f"**Repository:** {item['repo']} | **Date:** {item['date']}"
            if item.get('assets_count', 0) > 0:
                md += f" | **Assets:** {item['assets_count']}"
            md += "\n\n"
            
            md += f"[View Release]({item['url']})\n\n"
            
            # Highlights section
            highlights = item.get('highlights', {})
            has_highlights = any(highlights.values())
            
            if has_highlights:
                md += "#### 📌 Key Highlights\n\n"
                
                if highlights.get('breaking'):
                    md += "🚨 **Breaking Changes:**\n"
                    for change in highlights['breaking'][:2]:
                        md += f"- {change}\n"
                    md += "\n"
                
                if highlights.get('security'):
                    md += "🔒 **Security Updates:**\n"
                    for update in highlights['security'][:2]:
                        md += f"- {update}\n"
                    md += "\n"
                
                if highlights.get('features'):
                    md += "✨ **New Features:**\n"
                    for feature in highlights['features'][:2]:
                        md += f"- {feature}\n"
                    md += "\n"
                
                if highlights.get('fixes'):
                    md += "🐛 **Bug Fixes:**\n"
                    for fix in highlights['fixes'][:2]:
                        md += f"- {fix}\n"
                    md += "\n"
            
            # Body preview
            if item['body'] and not has_highlights:
                md += "#### Release Notes\n\n"
                md += f"{item['body']}\n\n"
            
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

    # Fetch GitHub releases
    releases = fetch_github_releases(config['github_releases'], days_back)

    # Sort by date (newest first)
    releases.sort(key=lambda x: x['date_obj'], reverse=True)

    # Generate markdown
    title = f"DevOps GitHub Releases - {report_type.title()}"
    markdown = generate_markdown(releases, title)

    # Output to stdout
    print(markdown)

    return 0


if __name__ == "__main__":
    sys.exit(main())
