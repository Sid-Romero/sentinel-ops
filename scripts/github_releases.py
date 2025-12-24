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

                release_info = {
                    'name': repo_config['name'],
                    'repo': repo,
                    'version': release.get('tag_name', 'Unknown'),
                    'title': release.get(
                        'name', release.get('tag_name', 'No title')),
                    'url': release.get('html_url', ''),
                    'date': published_at.strftime('%Y-%m-%d %H:%M'),
                    'category': repo_config['category'],
                    'prerelease': release.get('prerelease', False),
                    'body': release.get('body', '')[:300] + '...'
                    if release.get('body') else ''
                }
                releases.append(release_info)

        except Exception as e:
            print(
                f"Error fetching {
                    repo_config['repo']}: {e}",
                file=sys.stderr)

    return releases


def generate_markdown(releases: List[Dict], title: str) -> str:
    """Generate markdown output for releases"""
    md = f"# {title}\n\n"
    md += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*\n\n"

    if not releases:
        md += "No new releases found.\n"
        return md

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
        for item in items:
            prerelease_tag = " (Pre-release)" if item['prerelease'] else ""
            md += f"### {item['name']} {item['version']}{prerelease_tag}\n"
            md += f"**Repository:** {item['repo']} | **Date:** {item['date']}\n\n"
            md += f"[View Release]({item['url']})\n\n"
            if item['body']:
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
    releases.sort(key=lambda x: x['date'], reverse=True)

    # Generate markdown
    title = f"DevOps GitHub Releases - {report_type.title()}"
    markdown = generate_markdown(releases, title)

    # Output to stdout
    print(markdown)

    return 0


if __name__ == "__main__":
    sys.exit(main())
