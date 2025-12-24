#!/usr/bin/env python3
"""
Main aggregator script that combines all sources
"""
import sys
import subprocess
from datetime import datetime
from pathlib import Path
import re


def extract_summary_stats(content: str) -> dict:
    """Extract statistics from scraper outputs"""
    stats = {
        'rss_articles': 0,
        'rss_categories': 0,
        'releases': 0,
        'release_categories': 0,
        'hn_stories': 0,
        'hn_points': 0,
        'hn_comments': 0,
        'breaking_changes': 0,
        'security_updates': 0
    }
    
    # Extract RSS stats
    rss_match = re.search(r'📊 \*\*Total Articles:\*\* (\d+) \| \*\*Categories:\*\* (\d+)', content)
    if rss_match:
        stats['rss_articles'] = int(rss_match.group(1))
        stats['rss_categories'] = int(rss_match.group(2))
    
    # Extract release stats
    release_match = re.search(r'📦 \*\*Total Releases:\*\* (\d+) \| \*\*Categories:\*\* (\d+)', content)
    if release_match:
        stats['releases'] = int(release_match.group(1))
        stats['release_categories'] = int(release_match.group(2))
    
    # Count breaking changes
    stats['breaking_changes'] = content.count('with breaking changes')
    stats['security_updates'] = content.count('with security updates')
    
    # Extract HN stats
    hn_match = re.search(r'💬 \*\*Total Stories:\*\* (\d+) \| \*\*Total Points:\*\* (\d+) \| \*\*Total Comments:\*\* (\d+)', content)
    if hn_match:
        stats['hn_stories'] = int(hn_match.group(1))
        stats['hn_points'] = int(hn_match.group(2))
        stats['hn_comments'] = int(hn_match.group(3))
    
    return stats


def generate_executive_summary(stats: dict, report_type: str) -> str:
    """Generate an executive summary section"""
    summary = "# 📋 Executive Summary\n\n"
    summary += f"*{report_type.title()} DevOps Ecosystem Overview*\n\n"
    
    # Overall activity
    total_items = stats['rss_articles'] + stats['releases'] + stats['hn_stories']
    summary += f"## Activity Overview\n\n"
    summary += f"- 📰 **{stats['rss_articles']}** new articles from RSS feeds across **{stats['rss_categories']}** categories\n"
    summary += f"- 📦 **{stats['releases']}** new releases from monitored projects across **{stats['release_categories']}** categories\n"
    summary += f"- 💬 **{stats['hn_stories']}** relevant Hacker News discussions with **{stats['hn_points']}** points and **{stats['hn_comments']}** comments\n"
    summary += f"- 🎯 **{total_items}** total items tracked\n\n"
    
    # Important alerts
    if stats['breaking_changes'] > 0 or stats['security_updates'] > 0:
        summary += "## ⚠️ Important Alerts\n\n"
        if stats['breaking_changes'] > 0:
            summary += f"- 🚨 **{stats['breaking_changes']}** release(s) contain breaking changes - review before upgrading\n"
        if stats['security_updates'] > 0:
            summary += f"- 🔒 **{stats['security_updates']}** release(s) include security updates - consider upgrading\n"
        summary += "\n"
    
    summary += "---\n\n"
    
    return summary


def run_scraper(script_name: str, args: list = None) -> str:
    """Run a scraper script and return its output"""
    cmd = ["python3", f"scripts/{script_name}"]
    if args:
        cmd.extend(args)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        return f"# Error\n\nFailed to fetch data from {script_name}\n\n"


def generate_combined_report(report_type: str = "daily") -> str:
    """Generate a combined report from all sources"""
    args = ["--weekly"] if report_type == "weekly" else []

    print(f"Generating {report_type} report...", file=sys.stderr)

    # Fetch all content first
    print("Fetching RSS feeds...", file=sys.stderr)
    rss_content = run_scraper("rss_scraper.py", args)
    
    print("Fetching GitHub releases...", file=sys.stderr)
    releases_content = run_scraper("github_releases.py", args)
    
    print("Fetching Hacker News...", file=sys.stderr)
    hn_content = run_scraper("hacker_news.py", args)
    
    # Combine all content for stats extraction
    all_content = rss_content + "\n" + releases_content + "\n" + hn_content
    
    # Extract statistics
    stats = extract_summary_stats(all_content)
    
    # Build final report
    # Header
    report = f"# 🚀 DevOps Monitoring Digest - {report_type.title()}\n\n"
    report += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*\n\n"
    report += "**Your comprehensive source for DevOps ecosystem updates and insights**\n\n"
    report += "---\n\n"
    
    # Executive Summary
    report += generate_executive_summary(stats, report_type)

    # RSS Feeds
    report += rss_content + "\n\n"

    # GitHub Releases
    report += releases_content + "\n\n"

    # Hacker News
    report += hn_content + "\n\n"

    # Footer
    report += "---\n\n"
    report += "## 💡 About This Digest\n\n"
    report += "This automated report aggregates the latest DevOps news, tool releases, and community discussions to help you stay informed about the rapidly evolving DevOps ecosystem.\n\n"
    report += "**Sources:**\n"
    report += "- 📰 RSS Feeds: DevOps Weekly, CNCF Blog, HashiCorp Blog, The New Stack, DevOps.com, Kubernetes Blog, Docker Blog\n"
    report += "- 📦 GitHub Releases: Kubernetes, Terraform, Docker, Grafana, ArgoCD, Prometheus, Helm, Ansible\n"
    report += "- 💬 Hacker News: Curated DevOps discussions with high engagement\n\n"
    report += "*This report was automatically generated by Sentinel-Ops*\n"

    return report


def save_report(content: str, output_dir: str, filename: str):
    """Save report to file"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    file_path = output_path / filename
    with open(file_path, 'w') as f:
        f.write(content)

    print(f"Report saved to: {file_path}", file=sys.stderr)
    return file_path


def main():
    """Main execution function"""
    # Determine report type
    report_type = "daily"
    if len(sys.argv) > 1:
        if sys.argv[1] == "--weekly":
            report_type = "weekly"
        elif sys.argv[1] == "--tri-daily":
            report_type = "tri-daily"

    # Generate report
    report = generate_combined_report(report_type)

    # Determine output path
    # For tri-daily, include time in filename
    date_format = '%Y-%m-%d-%H%M' if report_type == "tri-daily" else '%Y-%m-%d'
    date_str = datetime.now().strftime(date_format)
    filename = f"digest-{date_str}.md"
    output_dir = f"output/{report_type}"

    # Save report
    save_report(report, output_dir, filename)

    # Also output to stdout for GitHub Actions
    print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
