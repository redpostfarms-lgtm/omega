# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# GATEKEEPER - Web Scraper
# Scrapes entire world: GitHub, open source, documentation
# Integrates with brain knowledge base

import requests
import json
import time
import sys
import io
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
ARCHIVED = BRAIN / 'Archived'
SCRAPE_DIR = ARCHIVED / 'scraped_data'
SCRAPE_DIR.mkdir(parents=True, exist_ok=True)

# Rate limiting
RATE_LIMIT_DELAY = 1.0  # seconds between requests
MAX_PAGES = 100  # max pages per domain

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Gatekeeper-Bot/1.0 (Educational Research)'
        })
        self.scraped_urls = set()
        self.scraped_data = []
        
    def scrape_github_repo(self, owner, repo, token=None):
        """Scrape a GitHub repository using GitHub API."""
        print(f"Scraping GitHub: {owner}/{repo}")
        
        base_url = f"https://api.github.com/repos/{owner}/{repo}"
        headers = {}
        if token:
            headers['Authorization'] = f'token {token}'
        
        try:
            # Get repo info
            repo_info = self.session.get(base_url, headers=headers, timeout=10)
            if repo_info.status_code != 200:
                print(f"  ❌ Failed to access repo: {repo_info.status_code}")
                return None
            
            repo_data = repo_info.json()
            
            # Get README
            readme_url = f"{base_url}/readme"
            readme = self.session.get(readme_url, headers=headers, timeout=10)
            readme_content = ""
            if readme.status_code == 200:
                import base64
                readme_data = readme.json()
                readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
            
            # Get all files (simplified - would need recursive tree API)
            contents_url = f"{base_url}/contents"
            contents = self.session.get(contents_url, headers=headers, timeout=10)
            files = []
            if contents.status_code == 200:
                files = contents.json()
            
            # Extract code files
            code_content = ""
            for file in files[:20]:  # Limit to first 20 files
                if file['type'] == 'file' and file['size'] < 100000:  # < 100KB
                    try:
                        file_url = file['download_url']
                        file_resp = self.session.get(file_url, timeout=10)
                        if file_resp.status_code == 200:
                            code_content += f"\n\n=== {file['name']} ===\n"
                            code_content += file_resp.text[:5000]  # First 5KB
                    except:
                        pass
            
            result = {
                'type': 'github_repo',
                'owner': owner,
                'repo': repo,
                'url': repo_data.get('html_url', ''),
                'description': repo_data.get('description', ''),
                'stars': repo_data.get('stargazers_count', 0),
                'language': repo_data.get('language', ''),
                'readme': readme_content,
                'code_samples': code_content,
                'scraped_at': datetime.now().isoformat()
            }
            
            self.scraped_data.append(result)
            print(f"  ✅ Scraped: {owner}/{repo}")
            time.sleep(RATE_LIMIT_DELAY)
            
            return result
            
        except Exception as e:
            print(f"  ❌ Error scraping {owner}/{repo}: {e}")
            return None
    
    def search_github(self, query, max_results=50, token=None, min_stars=500):
        """Search GitHub repositories with optional stars filter."""
        print(f"Searching GitHub for: {query}")
        
        # Add stars filter if not already in query
        if 'stars:' not in query and min_stars > 0:
            query = f"{query} stars:>={min_stars}"
        
        url = "https://api.github.com/search/repositories"
        params = {'q': query, 'sort': 'stars', 'order': 'desc', 'per_page': min(max_results, 100)}
        headers = {}
        if token:
            headers['Authorization'] = f'token {token}'
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"  ❌ Search failed: {response.status_code}")
                if response.status_code == 403:
                    print("  ⚠️  Rate limit exceeded. Use --token for higher limits.")
                return []
            
            results = response.json()
            repos = []
            
            # Limit to top 10-20 repos as specified
            limit = min(max_results, 20)
            for item in results.get('items', [])[:limit]:
                owner = item['owner']['login']
                repo = item['name']
                stars = item.get('stargazers_count', 0)
                print(f"  📦 Scraping: {owner}/{repo} ({stars} stars)")
                repo_data = self.scrape_github_repo(owner, repo, token)
                if repo_data:
                    repos.append(repo_data)
                time.sleep(RATE_LIMIT_DELAY)
            
            print(f"  ✅ Found {len(repos)} repositories")
            return repos
            
        except Exception as e:
            print(f"  ❌ Search error: {e}")
            return []
    
    def scrape_web_page(self, url, max_depth=2, current_depth=0):
        """Scrape a web page and follow links."""
        if url in self.scraped_urls or current_depth > max_depth:
            return None
        
        self.scraped_urls.add(url)
        print(f"Scraping: {url} (depth {current_depth})")
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return None
            
            # Extract text content
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(url, href)
                if urlparse(absolute_url).netloc == urlparse(url).netloc:
                    links.append(absolute_url)
            
            result = {
                'type': 'web_page',
                'url': url,
                'title': soup.title.string if soup.title else '',
                'text': text[:50000],  # Limit to 50KB
                'links': links[:20],  # First 20 links
                'scraped_at': datetime.now().isoformat()
            }
            
            self.scraped_data.append(result)
            print(f"  ✅ Scraped: {url}")
            
            # Recursively scrape linked pages
            if current_depth < max_depth:
                for link in links[:5]:  # Limit to 5 links per page
                    if link not in self.scraped_urls:
                        time.sleep(RATE_LIMIT_DELAY)
                        self.scrape_web_page(link, max_depth, current_depth + 1)
            
            return result
            
        except ImportError:
            print("  ⚠️  BeautifulSoup not installed. Install: pip install beautifulsoup4")
            return None
        except Exception as e:
            print(f"  ❌ Error scraping {url}: {e}")
            return None
    
    def scrape_open_source_docs(self, topics):
        """Scrape open source documentation sites."""
        print("Scraping open source documentation...")
        
        doc_sites = {
            'python': 'https://docs.python.org/3/',
            'numpy': 'https://numpy.org/doc/stable/',
            'pandas': 'https://pandas.pydata.org/docs/',
            'scikit-learn': 'https://scikit-learn.org/stable/',
            'tensorflow': 'https://www.tensorflow.org/api_docs',
            'pytorch': 'https://pytorch.org/docs/stable/',
        }
        
        results = []
        for topic in topics:
            if topic.lower() in doc_sites:
                url = doc_sites[topic.lower()]
                result = self.scrape_web_page(url, max_depth=1)
                if result:
                    results.append(result)
                time.sleep(RATE_LIMIT_DELAY)
        
        return results
    
    def save_scraped_data(self, filename=None):
        """Save all scraped data to JSON."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'scraped_data_{timestamp}.json'
        
        filepath = SCRAPE_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved {len(self.scraped_data)} items to: {filepath}")
        return filepath
    
    def integrate_with_brain(self):
        """Integrate scraped data into Gatekeeper brain."""
        brain_file = ARCHIVED / 'gatekeeper_brain.json'
        
        if not brain_file.exists():
            print("⚠️  Brain file not found. Run brain_prime.py first.")
            return
        
        try:
            with open(brain_file, 'r', encoding='utf-8') as f:
                brain = json.load(f)
            
            # Add scraped data to knowledge
            if 'scraped_knowledge' not in brain:
                brain['scraped_knowledge'] = []
            
            brain['scraped_knowledge'].extend(self.scraped_data)
            
            # Update timestamp
            brain['last_scrape'] = datetime.now().isoformat()
            brain['scrape_count'] = len(brain['scraped_knowledge'])
            
            with open(brain_file, 'w', encoding='utf-8') as f:
                json.dump(brain, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Integrated {len(self.scraped_data)} items into brain")
            
        except Exception as e:
            print(f"❌ Error integrating with brain: {e}")

def main():
    """Main scraping function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gatekeeper Web Scraper')
    parser.add_argument('--github', nargs='+', help='GitHub repos to scrape (owner/repo)')
    parser.add_argument('--search', help='GitHub search query')
    parser.add_argument('--url', help='Web page URL to scrape')
    parser.add_argument('--docs', nargs='+', help='Open source docs to scrape (python, numpy, etc.)')
    parser.add_argument('--token', help='GitHub API token (optional, increases rate limit)')
    parser.add_argument('--integrate', action='store_true', help='Integrate with brain after scraping')
    
    args = parser.parse_args()
    
    scraper = WebScraper()
    
    print("=" * 60)
    print("GATEKEEPER WEB SCRAPER")
    print("=" * 60)
    print()
    
    # Scrape GitHub repos
    if args.github:
        for repo_spec in args.github:
            if '/' in repo_spec:
                owner, repo = repo_spec.split('/', 1)
                scraper.scrape_github_repo(owner, repo, args.token)
    
    # Search GitHub
    if args.search:
        scraper.search_github(args.search, max_results=20, token=args.token)
    
    # Scrape web pages
    if args.url:
        scraper.scrape_web_page(args.url, max_depth=2)
    
    # Scrape documentation
    if args.docs:
        scraper.scrape_open_source_docs(args.docs)
    
    # Save data
    if scraper.scraped_data:
        scraper.save_scraped_data()
        
        # Integrate with brain
        if args.integrate:
            scraper.integrate_with_brain()
    else:
        print("\n⚠️  No data scraped. Use --github, --search, --url, or --docs")
        print("\nExamples:")
        print("  python web_scraper.py --github microsoft/vscode")
        print("  python web_scraper.py --search 'python automation'")
        print("  python web_scraper.py --url https://docs.python.org/")
        print("  python web_scraper.py --docs python numpy")

if __name__ == '__main__':
    main()

