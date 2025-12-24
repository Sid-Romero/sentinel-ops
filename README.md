# Sentinel-Ops

[![Tri-Daily Digest](https://github.com/Sid-Romero/sentinel-ops/actions/workflows/tri-daily-digest.yml/badge.svg)](https://github.com/Sid-Romero/sentinel-ops/actions/workflows/tri-daily-digest.yml)
[![Daily Digest](https://github.com/Sid-Romero/sentinel-ops/actions/workflows/daily-digest.yml/badge.svg)](https://github.com/Sid-Romero/sentinel-ops/actions/workflows/daily-digest.yml)
[![Weekly Digest](https://github.com/Sid-Romero/sentinel-ops/actions/workflows/weekly-digest.yml/badge.svg)](https://github.com/Sid-Romero/sentinel-ops/actions/workflows/weekly-digest.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Automated DevOps monitoring bot that aggregates news, releases, and discussions from multiple sources.

## Overview

Sentinel-Ops is an automated monitoring system that tracks the latest developments in the DevOps ecosystem. It collects information from RSS feeds, GitHub releases, and Hacker News, then generates tri-daily, daily, and weekly digest reports in Markdown format.

## Features

- **Tri-Daily Digest**: Automated reports three times per day at 6:00 AM, 2:00 PM, and 10:00 PM UTC
- **Daily Digest**: Automated daily reports at 6:00 AM UTC
- **Weekly Digest**: Comprehensive weekly summaries every Monday at 6:00 AM UTC
- **Enhanced Content Quality**:
  - Executive summaries with key statistics and alerts
  - Trending topics and tags extraction
  - Extended content previews (500+ characters for RSS, 600+ for releases)
  - Author information and reading time estimates
  - Changelog highlights extraction (breaking changes, security updates, features, fixes)
  - Categorized Hacker News discussions with trending indicators
- **RSS Feed Monitoring**: Tracks DevOps Weekly, CNCF Blog, HashiCorp Blog, The New Stack, DevOps.com, Kubernetes Blog, and Docker Blog
- **GitHub Releases**: Monitors releases for Kubernetes, Terraform, Docker, Grafana, ArgoCD, Prometheus, Helm, and Ansible
- **Hacker News Integration**: Curates top DevOps-related stories with high engagement
- **Automated Commits**: Results are automatically committed to the repository
- **Markdown Output**: All reports are generated in clean, readable Markdown format with emojis and visual indicators

## Structure

```
sentinel-ops/
├── .github/
│   └── workflows/
│       ├── tri-daily-digest.yml # Tri-daily automation workflow (3x/day)
│       ├── daily-digest.yml     # Daily automation workflow
│       └── weekly-digest.yml    # Weekly automation workflow
├── scripts/
│   ├── rss_scraper.py          # RSS feed scraper
│   ├── github_releases.py      # GitHub releases monitor
│   ├── hacker_news.py          # Hacker News scraper
│   └── generate_digest.py      # Main aggregator script
├── data/
│   └── sources.yml             # Configuration for all sources
├── output/
│   ├── tri-daily/              # Tri-daily digest reports (3x/day)
│   ├── daily/                  # Daily digest reports
│   └── weekly/                 # Weekly digest reports
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Configuration

The `data/sources.yml` file contains all configuration for monitored sources:

- **RSS Feeds**: List of RSS feed URLs with categories
- **GitHub Repositories**: Repositories to monitor for new releases
- **Hacker News Settings**: Keywords, minimum score threshold, and result limits

## Usage

### Manual Execution

Generate a tri-daily digest:
```bash
python scripts/generate_digest.py --tri-daily
```

Generate a daily digest:
```bash
python scripts/generate_digest.py
```

Generate a weekly digest:
```bash
python scripts/generate_digest.py --weekly
```

Run individual scrapers:
```bash
python scripts/rss_scraper.py
python scripts/github_releases.py
python scripts/hacker_news.py
```

### Automated Execution

The GitHub Actions workflows run automatically:
- **Tri-Daily**: Three times per day at 6:00 AM, 2:00 PM, and 10:00 PM UTC
- **Daily**: Every day at 6:00 AM UTC
- **Weekly**: Every Monday at 6:00 AM UTC

You can also trigger workflows manually from the Actions tab in GitHub.

## Requirements

- Python 3.11+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Sid-Romero/sentinel-ops.git
cd sentinel-ops
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run a digest:
```bash
python scripts/generate_digest.py
```

## Output

Reports are saved in the `output/` directory:
- `output/tri-daily/digest-YYYY-MM-DD-HHMM.md` - Tri-daily reports (3 times per day)
- `output/daily/digest-YYYY-MM-DD.md` - Daily reports
- `output/weekly/digest-YYYY-MM-DD.md` - Weekly reports

Each report includes:
- Executive summary with activity overview and important alerts
- RSS feed articles organized by category with:
  - Trending topics and tags
  - Author information and reading time estimates
  - Extended content previews
- Latest GitHub releases for monitored tools with:
  - Changelog highlights (breaking changes, security updates, features, fixes)
  - Asset information
  - Visual indicators for pre-releases and important updates
- Top Hacker News stories related to DevOps with:
  - Categorization by topic
  - Trending indicators
  - Engagement metrics

## Monitored Sources

### RSS Feeds
- DevOps Weekly Newsletter
- CNCF Blog
- HashiCorp Blog
- The New Stack
- DevOps.com
- Kubernetes Blog
- Docker Blog

### GitHub Projects
- Kubernetes
- Terraform
- Docker CLI
- Grafana
- ArgoCD
- Prometheus
- Helm
- Ansible

### Hacker News Topics
- DevOps
- Kubernetes
- Terraform
- Docker
- CI/CD
- GitOps
- Observability
- Infrastructure as Code
- Site Reliability Engineering

## Contributing

Contributions are welcome! To add new sources:

1. Update `data/sources.yml` with new RSS feeds or GitHub repositories
2. For new source types, create a new scraper in the `scripts/` directory
3. Update `scripts/generate_digest.py` to include the new source

## License

MIT License - see LICENSE file for details

## Authors

Automated monitoring bot created for the DevOps community.