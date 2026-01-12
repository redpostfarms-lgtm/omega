#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# STRESS TEST SIMPLE 2026 – BREAK IT, FIX IT
# Simple stress test that actually works

import sys
import io
import time
import threading
import json
import traceback
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import random

# Set UTF-8 encoding
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

ROOT = Path(r'D:\RPF_BRAIN')
GATEKEEPER = ROOT / 'The Gatekeeper'

RESULTS = {
    'tests': [],
    'breaking_points': [],
    'performance': {}
}

class SimpleStressTest:
    """Simple stress test."""
    
    def __init__(self):
        self.start = time.time()
        self.count = 0
        self.passed = 0
        self.failed = 0
        
        print("=" * 100)
        print("GATEKEEPER STRESS TEST - SIMPLE VERSION")
        print("=" * 100)
        print(f"Start: {datetime.now().strftime('%H:%M:%S')}\n")
    
    def test(self, name, func):
        """Run a test."""
        self.count += 1
        try:
            result = func()
            if result:
                self.passed += 1
                print(f"✅ [{self.count}] {name}: PASS")
                RESULTS['tests'].append({'test': name, 'status': 'PASS'})
                return True
            else:
                self.failed += 1
                print(f"❌ [{self.count}] {name}: FAIL")
                RESULTS['tests'].append({'test': name, 'status': 'FAIL'})
                RESULTS['breaking_points'].append({'test': name, 'issue': 'Test returned False'})
                return False
        except Exception as e:
            self.failed += 1
            print(f"❌ [{self.count}] {name}: FAIL - {e}")
            RESULTS['tests'].append({'test': name, 'status': 'FAIL', 'error': str(e)})
            RESULTS['breaking_points'].append({'test': name, 'issue': str(e), 'traceback': traceback.format_exc()})
            return False
    
    def test_import(self):
        """Test import."""
        def _test():
            sys.path.insert(0, str(GATEKEEPER))
            from FarmOS_2026 import AGENTS_REGISTRY
            return len(AGENTS_REGISTRY) >= 6
        return self.test("Import", _test)
    
    def test_concurrent(self, num=50):
        """Test concurrent queries."""
        def _test():
            from FarmOS_2026 import AgentBus
            bus = AgentBus()
            
            errors = []
            success = 0
            
            def worker(i):
                nonlocal success, errors
                try:
                    agent = random.choice(['harriet', 'bob', 'apothecary', 'feedmaster', 'medical', 'salesbot'])
                    response = bus.ask(agent, f"test {i}")
                    if response:
                        success += 1
                    else:
                        errors.append(f"Empty response {i}")
                except Exception as e:
                    errors.append(f"Error {i}: {e}")
            
            threads = []
            for i in range(num):
                t = threading.Thread(target=worker, args=(i,))
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join(timeout=5)
            
            rate = success / num if num > 0 else 0
            if rate < 0.8:
                RESULTS['breaking_points'].append({
                    'test': 'Concurrent',
                    'issue': f'Low success rate: {rate*100:.1f}%',
                    'errors': errors[:5]
                })
            return rate >= 0.8
        
        return self.test(f"Concurrent ({num} queries)", _test)
    
    def test_agents(self, iterations=20):
        """Test agent functions."""
        def _test():
            from FarmOS_2026 import (
                harriet_agent, bob_agent, apothecary_agent,
                feedmaster_agent, medical_agent, salesbot_agent
            )
            
            agents = [
                ('harriet', harriet_agent, "new hire"),
                ('bob', bob_agent, "pole barn"),
                ('apothecary', apothecary_agent, "aphids"),
                ('feedmaster', feedmaster_agent, "layers"),
                ('medical', medical_agent, "fall"),
                ('salesbot', salesbot_agent, "order")
            ]
            
            success = 0
            total = iterations * len(agents)
            
            for i in range(iterations):
                for name, func, query in agents:
                    try:
                        result = func(query)
                        if result:
                            success += 1
                    except:
                        pass
            
            rate = success / total if total > 0 else 0
            if rate < 0.8:
                RESULTS['breaking_points'].append({
                    'test': 'Agent Functions',
                    'issue': f'Low success rate: {rate*100:.1f}%'
                })
            return rate >= 0.8
        
        return self.test(f"Agent Functions ({iterations} iterations)", _test)
    
    def test_knowledge(self, num=30):
        """Test quantum knowledge."""
        def _test():
            from FarmOS_2026 import quantum_knowledge
            
            queries = ["HR law", "pole barn", "pest control", "feed", "medical"] * (num // 5)
            success = 0
            
            for query in queries:
                try:
                    result = quantum_knowledge(query)
                    if result:
                        success += 1
                except:
                    pass
            
            rate = success / num if num > 0 else 0
            if rate < 0.9:
                RESULTS['breaking_points'].append({
                    'test': 'Quantum Knowledge',
                    'issue': f'Low success rate: {rate*100:.1f}%'
                })
            return rate >= 0.9
        
        return self.test(f"Quantum Knowledge ({num} queries)", _test)
    
    def test_errors(self):
        """Test error handling."""
        def _test():
            from FarmOS_2026 import AgentBus, quantum_knowledge
            bus = AgentBus()
            
            # Should not crash on invalid inputs
            try:
                bus.ask('invalid', 'test')
                quantum_knowledge("")
                quantum_knowledge(None)
                return True
            except:
                return False
        
        return self.test("Error Handling", _test)
    
    def run_all(self):
        """Run all tests."""
        print("Running tests...\n")
        
        self.test_import()
        self.test_concurrent(num=50)
        self.test_agents(iterations=20)
        self.test_knowledge(num=30)
        self.test_errors()
        
        self.summary()
    
    def summary(self):
        """Print summary."""
        elapsed = time.time() - self.start
        
        print("\n" + "=" * 100)
        print("SUMMARY")
        print("=" * 100)
        print(f"Tests: {self.count} | Passed: {self.passed} | Failed: {self.failed}")
        print(f"Time: {elapsed:.2f}s")
        
        if RESULTS['breaking_points']:
            print(f"\nBREAKING POINTS ({len(RESULTS['breaking_points'])}):")
            for i, bp in enumerate(RESULTS['breaking_points'], 1):
                print(f"  {i}. {bp['test']}: {bp['issue']}")
        
        # Save
        results_file = GATEKEEPER / 'stress_test_results.json'
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(RESULTS, f, indent=2, default=str)
            print(f"\nResults saved: {results_file}")
        except Exception as e:
            print(f"\nCould not save: {e}")
        
        print("=" * 100)

if __name__ == '__main__':
    test = SimpleStressTest()
    test.run_all()

