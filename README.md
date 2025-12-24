# Sentinel-Ops

[![Daily Digest](https://github.com/Sid-Romero/sentinel-ops/actions/workflows/daily-digest.yml/badge.svg)](https://github.com/Sid-Romero/sentinel-ops/actions/workflows/daily-digest.yml)
[![Weekly Digest](https://github.com/Sid-Romero/sentinel-ops/actions/workflows/weekly-digest.yml/badge.svg)](https://github.com/Sid-Romero/sentinel-ops/actions/workflows/weekly-digest.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Automated DevOps monitoring bot that aggregates news, releases, and discussions from multiple sources.

## Overview

Sentinel-Ops is an automated monitoring system that tracks the latest developments in the DevOps ecosystem. It collects information from RSS feeds, GitHub releases, and Hacker News, then generates daily and weekly digest reports in Markdown format.

## Features

- **Daily Digest**: Automated daily reports at 6:00 AM UTC
- **Weekly Digest**: Comprehensive weekly summaries every Monday at 6:00 AM UTC
- **RSS Feed Monitoring**: Tracks DevOps Weekly, CNCF Blog, and HashiCorp Blog
- **GitHub Releases**: Monitors releases for Kubernetes, Terraform, Docker, Grafana, and ArgoCD
- **Hacker News Integration**: Curates top DevOps-related stories with high engagement
- **Automated Commits**: Results are automatically committed to the repository
- **Markdown Output**: All reports are generated in clean, readable Markdown format

## Structure

```
sentinel-ops/
├── .github/
│   └── workflows/
│       ├── daily-digest.yml    # Daily automation workflow
│       └── weekly-digest.yml   # Weekly automation workflow
├── scripts/
│   ├── rss_scraper.py         # RSS feed scraper
│   ├── github_releases.py     # GitHub releases monitor
│   ├── hacker_news.py         # Hacker News scraper
│   └── generate_digest.py     # Main aggregator script
├── data/
│   └── sources.yml            # Configuration for all sources
├── output/
│   ├── daily/                 # Daily digest reports
│   └── weekly/                # Weekly digest reports
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Configuration

The `data/sources.yml` file contains all configuration for monitored sources:

- **RSS Feeds**: List of RSS feed URLs with categories
- **GitHub Repositories**: Repositories to monitor for new releases
- **Hacker News Settings**: Keywords, minimum score threshold, and result limits

## Usage

### Manual Execution

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
- `output/daily/digest-YYYY-MM-DD.md` - Daily reports
- `output/weekly/digest-YYYY-MM-DD.md` - Weekly reports

Each report includes:
- RSS feed articles organized by category
- Latest GitHub releases for monitored tools
- Top Hacker News stories related to DevOps

## Monitored Sources

### RSS Feeds
- DevOps Weekly Newsletter
- CNCF Blog
- HashiCorp Blog

### GitHub Projects
- Kubernetes
- Terraform
- Docker CLI
- Grafana
- ArgoCD

### Hacker News Topics
- DevOps
- Kubernetes
- Terraform
- Docker
- CI/CD
- GitOps
- Observability

## Contributing

Contributions are welcome! To add new sources:

1. Update `data/sources.yml` with new RSS feeds or GitHub repositories
2. For new source types, create a new scraper in the `scripts/` directory
3. Update `scripts/generate_digest.py` to include the new source

## License

MIT License - see LICENSE file for details

## Authors

Automated monitoring bot created for the DevOps community.