# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Async HTTP Client with Rate Limiting - Legitimate Use Cases Only
#
# Purpose: Efficient HTTP requests with proper rate limiting
# Use for: Your own APIs, authorized testing, legitimate web scraping

import asyncio
import aiohttp
import time
from typing import List, Dict, Any, Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)

class RateLimitedHTTPClient:
    """Rate-limited async HTTP client for legitimate use cases.
    
    Use for:
    - Communicating with your own APIs
    - Authorized web scraping (with permission)
    - Load testing your own applications
    - Monitoring your own infrastructure
    
    NOT for:
    - Evading rate limits on unauthorized systems
    - Bypassing security controls
    - Automated attacks
    """
    
    def __init__(self, requests_per_second: float = 10.0, max_concurrent: int = 5):
        """Initialize rate-limited HTTP client.
        
        Args:
            requests_per_second: Maximum requests per second
            max_concurrent: Maximum concurrent requests
        """
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.max_concurrent = max_concurrent
        self.request_times = deque(maxlen=int(requests_per_second * 2))
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limit."""
        now = time.time()
        
        # Remove old request times
        while self.request_times and self.request_times[0] < now - 1.0:
            self.request_times.popleft()
        
        # Check if we need to wait
        if len(self.request_times) >= self.requests_per_second:
            # Calculate wait time
            oldest_request = self.request_times[0]
            wait_time = 1.0 - (now - oldest_request)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.request_times.append(time.time())
    
    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """Make rate-limited GET request.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments for aiohttp
        
        Returns:
            Dictionary with response data
        """
        async with self.semaphore:
            await self._wait_for_rate_limit()
            
            try:
                async with self.session.get(url, **kwargs) as response:
                    text = await response.text()
                    return {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "text": text,
                        "url": str(response.url)
                    }
            except Exception as e:
                logger.error(f"Request failed: {e}")
                return {
                    "status": 0,
                    "error": str(e),
                    "url": url
                }
    
    async def post(self, url: str, data: Any = None, json: Any = None, **kwargs) -> Dict[str, Any]:
        """Make rate-limited POST request.
        
        Args:
            url: URL to request
            data: Form data
            json: JSON data
            **kwargs: Additional arguments for aiohttp
        
        Returns:
            Dictionary with response data
        """
        async with self.semaphore:
            await self._wait_for_rate_limit()
            
            try:
                async with self.session.post(url, data=data, json=json, **kwargs) as response:
                    text = await response.text()
                    return {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "text": text,
                        "url": str(response.url)
                    }
            except Exception as e:
                logger.error(f"Request failed: {e}")
                return {
                    "status": 0,
                    "error": str(e),
                    "url": url
                }
    
    async def fetch_multiple(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Fetch multiple URLs with rate limiting.
        
        Args:
            urls: List of URLs to fetch
            **kwargs: Additional arguments for requests
        
        Returns:
            List of response dictionaries
        """
        tasks = [self.get(url, **kwargs) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error dictionaries
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "status": 0,
                    "error": str(result),
                    "url": urls[i]
                })
            else:
                processed_results.append(result)
        
        return processed_results


async def example_usage():
    """Example usage (legitimate HTTP requests)."""
    print("Rate-Limited HTTP Client - Legitimate Use Cases Only")
    print("=" * 60)
    
    # Example: Request your own API
    async with RateLimitedHTTPClient(requests_per_second=5.0) as client:
        # Example URLs (replace with your own)
        test_urls = [
            "https://httpbin.org/get",  # Test endpoint
            "https://httpbin.org/get",
            "https://httpbin.org/get",
        ]
        
        print(f"Making {len(test_urls)} requests with rate limiting...")
        start = time.time()
        
        results = await client.fetch_multiple(test_urls)
        
        elapsed = time.time() - start
        print(f"Completed in {elapsed:.2f}s")
        print(f"Average time per request: {elapsed/len(test_urls):.2f}s")
        
        for i, result in enumerate(results):
            print(f"\nRequest {i+1}:")
            print(f"  Status: {result.get('status', 'N/A')}")
            print(f"  URL: {result.get('url', 'N/A')}")
            if 'error' in result:
                print(f"  Error: {result['error']}")
    
    print("\n✅ Legitimate HTTP requests complete")


def main():
    """Main entry point."""
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example_usage())


if __name__ == '__main__':
    main()
