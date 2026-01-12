# Gatekeeper Web Scraping Guide

## Overview

The Gatekeeper can scrape the entire world: GitHub repositories, open source documentation, and web pages. All scraped data integrates directly into the brain knowledge base.

## Quick Start

### Install Dependencies
```bash
pip install requests beautifulsoup4
```

### Basic Usage

#### Scrape a Single GitHub Repository
```bash
python "The Gatekeeper\web_scraper.py" --github microsoft/vscode --integrate
```

#### Search GitHub
```bash
python "The Gatekeeper\web_scraper.py" --search "python automation" --integrate
```

#### Scrape a Web Page
```bash
python "The Gatekeeper\web_scraper.py" --url https://docs.python.org/ --integrate
```

#### Scrape Documentation
```bash
python "The Gatekeeper\web_scraper.py" --docs python numpy pandas --integrate
```

## Mass Scraping

### Run Mass Scraper
```bash
python "The Gatekeeper\mass_scrape.py"
```

This will:
1. Scrape top GitHub repositories (Python, Automation, AI/ML, Farm/Ag, Solar)
2. Scrape open source documentation sites
3. Search GitHub for relevant topics
4. Save everything to `Archived/scraped_data/`
5. Integrate with brain knowledge base

**Warning**: This takes a long time and makes many requests. Use a GitHub token for faster scraping.

## GitHub API Token (Optional but Recommended)

1. Create token: https://github.com/settings/tokens
2. Use with scraper:
```bash
python "The Gatekeeper\web_scraper.py" --github owner/repo --token YOUR_TOKEN
```

Benefits:
- Higher rate limit (5000 requests/hour vs 60)
- Access to private repos (if you have access)
- Faster scraping

## Categories Scraped

### GitHub Repositories
- **Python**: cpython, requests, numpy, pandas, scikit-learn
- **Automation**: vscode, ansible, terraform, kubernetes
- **AI/ML**: tensorflow, pytorch, transformers, gpt-3
- **Farm/Ag**: farmbot, OpenFarm, agri-lab
- **Solar**: pvlib, pvwatts, emonpi

### Documentation Sites
- Python official docs
- NumPy documentation
- Pandas documentation
- Scikit-learn docs
- TensorFlow API
- PyTorch docs

### Search Topics
- python farm automation
- solar panel monitoring
- battery management system
- 18650 battery
- USDA grant application
- off-grid solar
- drone agriculture
- crop monitoring
- quantum cryptography
- post-quantum encryption

## Output

All scraped data is saved to:
- `D:\RPF_BRAIN\Archived\scraped_data\scraped_data_YYYYMMDD_HHMMSS.json`

And integrated into:
- `D:\RPF_BRAIN\Archived\gatekeeper_brain.json`

## Rate Limiting

The scraper includes:
- 1 second delay between requests (configurable)
- Respects GitHub API rate limits
- Max 100 pages per domain
- Max 20 files per repository

## Examples

### Scrape Multiple Repos
```bash
python "The Gatekeeper\web_scraper.py" --github microsoft/vscode python/cpython numpy/numpy --integrate
```

### Search and Scrape
```bash
python "The Gatekeeper\web_scraper.py" --search "solar battery" --token YOUR_TOKEN --integrate
```

### Comprehensive Scrape
```bash
python "The Gatekeeper\mass_scrape.py"
```

## Integration with Brain

Use `--integrate` flag to automatically add scraped data to the Gatekeeper brain:
```bash
python "The Gatekeeper\web_scraper.py" --github owner/repo --integrate
```

The brain will be updated with:
- Repository information
- Code samples
- Documentation
- All scraped knowledge

## Notes

- **Respect rate limits**: Don't hammer servers
- **Use tokens**: GitHub tokens increase rate limits
- **Be patient**: Mass scraping takes time
- **Check results**: Verify data quality before integration

## The Gatekeeper Knows More

After scraping, the Gatekeeper has knowledge from:
- ✅ GitHub repositories
- ✅ Open source documentation
- ✅ Web pages
- ✅ Code samples
- ✅ Documentation

**The doors of knowledge opens wider. The Gatekeeper sees more.**

