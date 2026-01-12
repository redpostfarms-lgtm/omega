# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# GATEKEEPER - Mass Scraper
# Scrapes entire world: GitHub, open source, documentation
# Comprehensive knowledge gathering

import subprocess
import sys
import io
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def mass_scrape_github():
    """Mass scrape popular GitHub repositories."""
    print("=" * 60)
    print("MASS GITHUB SCRAPING")
    print("=" * 60)
    
    # Top repositories by category
    repos = {
        'python': [
            'python/cpython',
            'psf/requests',
            'numpy/numpy',
            'pandas-dev/pandas',
            'scikit-learn/scikit-learn',
        ],
        'automation': [
            'microsoft/vscode',
            'ansible/ansible',
            'hashicorp/terraform',
            'kubernetes/kubernetes',
        ],
        'ai_ml': [
            'tensorflow/tensorflow',
            'pytorch/pytorch',
            'huggingface/transformers',
            'openai/gpt-3',
        ],
        'farm_ag': [
            'farmbot/farmbot_os',
            'openfarmcc/OpenFarm',
            'AgriLab/agri-lab',
        ],
        'solar_energy': [
            'pvlib/pvlib-python',
            'NREL/pvwatts',
            'openenergymonitor/emonpi',
        ],
    }
    
    from web_scraper import WebScraper
    scraper = WebScraper()
    
    total = 0
    for category, repo_list in repos.items():
        print(f"\n📦 Category: {category}")
        for repo in repo_list:
            owner, repo_name = repo.split('/')
            result = scraper.scrape_github_repo(owner, repo_name)
            if result:
                total += 1
    
    print(f"\n✅ Scraped {total} repositories")
    return scraper

def mass_scrape_docs():
    """Mass scrape open source documentation."""
    print("\n" + "=" * 60)
    print("MASS DOCUMENTATION SCRAPING")
    print("=" * 60)
    
    from web_scraper import WebScraper
    scraper = WebScraper()
    
    docs = [
        'python',
        'numpy',
        'pandas',
        'scikit-learn',
    ]
    
    results = scraper.scrape_open_source_docs(docs)
    print(f"\n✅ Scraped {len(results)} documentation sites")
    return scraper

def mass_scrape_searches():
    """Mass search GitHub for relevant topics."""
    print("\n" + "=" * 60)
    print("MASS GITHUB SEARCHES")
    print("=" * 60)
    
    from web_scraper import WebScraper
    scraper = WebScraper()
    
    searches = [
        'python farm automation',
        'solar panel monitoring',
        'battery management system',
        '18650 battery',
        'USDA grant application',
        'off-grid solar',
        'drone agriculture',
        'crop monitoring',
        'quantum cryptography',
        'post-quantum encryption',
    ]
    
    total = 0
    for query in searches:
        print(f"\n🔍 Searching: {query}")
        repos = scraper.search_github(query, max_results=5)
        total += len(repos)
    
    print(f"\n✅ Found {total} repositories from searches")
    return scraper

def scrape_category(category):
    """Scrape a specific category."""
    print(f"=" * 60)
    print(f"SCRAPING CATEGORY: {category}")
    print(f"=" * 60)
    
    from web_scraper import WebScraper
    scraper = WebScraper()
    
    # Map category to search terms and docs
    category_map = {
        'quantum': {
            'search': ['quantum computing', 'quantum cryptography', 'qiskit', 'post-quantum'],
            'docs': []
        },
        'solar': {
            'search': ['solar panel monitoring', 'solar energy', 'pvlib', 'solar forecasting'],
            'docs': []
        },
        'battery': {
            'search': ['battery management', '18650', 'lithium ion', 'battery monitoring'],
            'docs': []
        },
        'off-grid': {
            'search': ['off-grid solar', 'off-grid power', 'solar battery bank'],
            'docs': []
        },
        'farm': {
            'search': ['farm automation', 'agriculture technology', 'precision agriculture'],
            'docs': []
        },
        'drone': {
            'search': ['drone agriculture', 'crop monitoring', 'NDVI', 'agricultural drone'],
            'docs': []
        },
    }
    
    # Use category or treat as search term
    if category.lower() in category_map:
        config = category_map[category.lower()]
        searches = config['search']
    else:
        # Treat category as search term
        searches = [category]
    
    total = 0
    for search_term in searches:
        print(f"\n🔍 Searching: {search_term}")
        repos = scraper.search_github(f"{search_term} stars:>500", max_results=10, token=None)
        total += len(repos)
    
    print(f"\n✅ Scraped {total} repositories for category: {category}")
    return scraper

def deep_scrape():
    """Deep scraping mode - comprehensive knowledge gathering."""
    print("=" * 60)
    print("GATEKEEPER - DEEP SCRAPING MODE")
    print("Comprehensive planetary knowledge refresh")
    print("=" * 60)
    print("\nRunning deep scrape (no prompts, auto-execute)...\n")
    
    # Run all scraping operations without prompts
    all_data = []
    
    # 1. Mass GitHub repos
    scraper1 = mass_scrape_github()
    all_data.extend(scraper1.scraped_data)
    
    # 2. Mass documentation
    scraper2 = mass_scrape_docs()
    all_data.extend(scraper2.scraped_data)
    
    # 3. Mass searches
    scraper3 = mass_scrape_searches()
    all_data.extend(scraper3.scraped_data)
    
    # Combine all data
    from web_scraper import WebScraper
    final_scraper = WebScraper()
    final_scraper.scraped_data = all_data
    
    # Save everything
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = final_scraper.save_scraped_data(f'deep_scrape_{timestamp}.json')
    
    # Integrate with brain
    print("\n" + "=" * 60)
    print("INTEGRATING WITH BRAIN")
    print("=" * 60)
    final_scraper.integrate_with_brain()
    
    print("\n" + "=" * 60)
    print("✅ DEEP SCRAPING COMPLETE")
    print("=" * 60)
    print(f"Total items scraped: {len(all_data)}")
    print(f"Data saved to: {filepath}")
    print("\nThe Gatekeeper now knows more about the world.")
    
    return final_scraper

def main():
    """Run mass scraping operation."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gatekeeper Mass Scraper')
    parser.add_argument('--category', help='Scrape specific category')
    parser.add_argument('--deep', action='store_true', help='Deep scraping mode (no prompts, auto-execute)')
    
    args = parser.parse_args()
    
    # Deep mode - no prompts, auto-execute
    if args.deep:
        deep_scrape()
        return
    
    # If category specified, scrape just that
    if args.category:
        scraper = scrape_category(args.category)
        if scraper.scraped_data:
            scraper.save_scraped_data(f'category_{args.category}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            scraper.integrate_with_brain()
        return
    
    # Otherwise, full mass scrape
    print("=" * 60)
    print("GATEKEEPER - MASS WEB SCRAPER")
    print("Scraping entire world: GitHub + Open Source")
    print("=" * 60)
    print("\n⚠️  This will take a long time and make many requests.")
    print("⚠️  Respect rate limits. Use GitHub token for faster scraping.")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return
    
    # Run all scraping operations
    all_data = []
    
    # 1. Mass GitHub repos
    scraper1 = mass_scrape_github()
    all_data.extend(scraper1.scraped_data)
    
    # 2. Mass documentation
    scraper2 = mass_scrape_docs()
    all_data.extend(scraper2.scraped_data)
    
    # 3. Mass searches
    scraper3 = mass_scrape_searches()
    all_data.extend(scraper3.scraped_data)
    
    # Combine all data
    from web_scraper import WebScraper
    final_scraper = WebScraper()
    final_scraper.scraped_data = all_data
    
    # Save everything
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = final_scraper.save_scraped_data(f'mass_scrape_{timestamp}.json')
    
    # Integrate with brain
    print("\n" + "=" * 60)
    print("INTEGRATING WITH BRAIN")
    print("=" * 60)
    final_scraper.integrate_with_brain()
    
    print("\n" + "=" * 60)
    print("✅ MASS SCRAPING COMPLETE")
    print("=" * 60)
    print(f"Total items scraped: {len(all_data)}")
    print(f"Data saved to: {filepath}")
    print("\nThe Gatekeeper now knows more about the world.")

if __name__ == '__main__':
    main()

