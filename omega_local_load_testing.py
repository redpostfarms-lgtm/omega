"""
OMEGA Local Load Testing Alternative
=====================================
Workaround for Azure Load Testing - Uses local tools instead of Azure extension

Alternative Approaches (No Azure/Tokens Required):
1. Locust - Python-based load testing (pip install locust)
2. Apache JMeter - Java-based (download from apache.org)
3. K6 - Modern load testing (download from k6.io)
4. Python requests + threading - Custom solution

This module provides local load testing using built-in Python libraries.
"""

import concurrent.futures
import time
import requests
from typing import Dict, List, Callable, Optional
from datetime import datetime
import statistics
import json

class OmegaLocalLoadTester:
    """
    Local load testing tool - replacement for Azure Load Testing
    Uses Python's built-in threading and requests library
    """
    
    def __init__(self, target_url: str, concurrent_users: int = 10):
        self.target_url = target_url
        self.concurrent_users = concurrent_users
        self.results = []
        
    def single_request(self, request_id: int) -> Dict:
        """Execute single HTTP request and measure response time"""
        start_time = time.time()
        try:
            response = requests.get(self.target_url, timeout=30)
            end_time = time.time()
            
            return {
                'request_id': request_id,
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'success': response.status_code == 200,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            end_time = time.time()
            return {
                'request_id': request_id,
                'status_code': 0,
                'response_time': end_time - start_time,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_load_test(self, total_requests: int = 100, duration_seconds: Optional[int] = None) -> Dict:
        """
        Run load test with concurrent users
        
        Args:
            total_requests: Total number of requests to make
            duration_seconds: Alternative - run for specific duration
        
        Returns:
            Dictionary with test results and statistics
        """
        print(f"🔴 OMEGA Load Test Starting...")
        print(f"   Target: {self.target_url}")
        print(f"   Concurrent Users: {self.concurrent_users}")
        print(f"   Total Requests: {total_requests}")
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrent_users) as executor:
            futures = [executor.submit(self.single_request, i) for i in range(total_requests)]
            self.results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        
        response_times = [r['response_time'] for r in self.results]
        successful_requests = sum(1 for r in self.results if r['success'])
        failed_requests = len(self.results) - successful_requests
        
        stats = {
            'test_duration': end_time - start_time,
            'total_requests': len(self.results),
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'success_rate': (successful_requests / len(self.results)) * 100,
            'avg_response_time': statistics.mean(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'median_response_time': statistics.median(response_times),
            'requests_per_second': len(self.results) / (end_time - start_time)
        }
        
        self._print_results(stats)
        return stats
    
    def _print_results(self, stats: Dict):
        """Print formatted test results"""
        print(f"\n{'='*60}")
        print(f"🔴 OMEGA LOAD TEST RESULTS")
        print(f"{'='*60}")
        print(f"Duration:              {stats['test_duration']:.2f}s")
        print(f"Total Requests:        {stats['total_requests']}")
        print(f"Successful:            {stats['successful_requests']} ({stats['success_rate']:.1f}%)")
        print(f"Failed:                {stats['failed_requests']}")
        print(f"Requests/Second:       {stats['requests_per_second']:.2f}")
        print(f"\nResponse Times:")
        print(f"  Average:             {stats['avg_response_time']*1000:.2f}ms")
        print(f"  Median:              {stats['median_response_time']*1000:.2f}ms")
        print(f"  Min:                 {stats['min_response_time']*1000:.2f}ms")
        print(f"  Max:                 {stats['max_response_time']*1000:.2f}ms")
        print(f"{'='*60}\n")
    
    def save_results(self, filename: str = "load_test_results.json"):
        """Save detailed results to JSON file"""
        output = {
            'test_config': {
                'target_url': self.target_url,
                'concurrent_users': self.concurrent_users
            },
            'results': self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"✓ Results saved to {filename}")

LOAD_TESTING_ALTERNATIVES = {
    "locust": {
        "name": "Locust",
        "install": "pip install locust",
        "usage": "locust -f locustfile.py --host=http://localhost:5000",
        "docs": "https://docs.locust.io/",
        "free": True,
        "local": True
    },
    "k6": {
        "name": "K6",
        "install": "Download from https://k6.io/docs/get-started/installation/",
        "usage": "k6 run script.js",
        "docs": "https://k6.io/docs/",
        "free": True,
        "local": True
    },
    "jmeter": {
        "name": "Apache JMeter",
        "install": "Download from https://jmeter.apache.org/download_jmeter.cgi",
        "usage": "jmeter -n -t testplan.jmx",
        "docs": "https://jmeter.apache.org/usermanual/",
        "free": True,
        "local": True
    },
    "artillery": {
        "name": "Artillery",
        "install": "npm install -g artillery",
        "usage": "artillery quick --count 10 --num 100 http://localhost:5000",
        "docs": "https://www.artillery.io/docs",
        "free": True,
        "local": True
    }
}

def print_alternatives():
    """Print available load testing alternatives"""
    print("\n🔴 OMEGA LOAD TESTING ALTERNATIVES (No Azure Required)")
    print("="*70)
    
    for key, tool in LOAD_TESTING_ALTERNATIVES.items():
        print(f"\n{tool['name']}:")
        print(f"  Install: {tool['install']}")
        print(f"  Usage:   {tool['usage']}")
        print(f"  Docs:    {tool['docs']}")
        print(f"  Free:    ✓ Yes")
        print(f"  Local:   ✓ Yes")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    print_alternatives()
    
    tester = OmegaLocalLoadTester(
        target_url="http://127.0.0.1:5000",
        concurrent_users=5
    )
    
    results = tester.run_load_test(total_requests=50)
    tester.save_results()
