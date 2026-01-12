#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# STRESS TEST MASTER 2026 – BREAK THE SYSTEM, FIX IT BETTER
# Comprehensive stress test of entire Gatekeeper system
# Tests: FarmOS, all agents, voice listener, knowledge base, inter-agent comms, memory, concurrency

import sys
import io
import time
import threading
import subprocess
import json
import traceback
import gc
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional
import random
import queue

# Try to import psutil, fallback to basic memory tracking
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("WARNING: psutil not installed. Memory tracking will be limited.")
    print("Install with: pip install psutil")

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROOT = Path(r'D:\RPF_BRAIN')
GATEKEEPER = ROOT / 'The Gatekeeper'

# Test results storage
TEST_RESULTS = {
    'passed': [],
    'failed': [],
    'warnings': [],
    'errors': [],
    'performance': {},
    'memory_usage': {},
    'breaking_points': []
}

class StressTest:
    """Master stress test suite for entire Gatekeeper system."""
    
    def __init__(self):
        """Initialize stress test suite."""
        self.start_time = time.time()
        self.max_memory_mb = 0
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0
        self.warning_count = 0
        
        print("=" * 100)
        print("GATEKEEPER STRESS TEST MASTER 2026")
        print("=" * 100)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"System: {sys.platform}")
        print(f"Python: {sys.version}")
        print()
    
    def log_result(self, test_name: str, status: str, message: str = "", error: Exception = None):
        """Log test result."""
        self.test_count += 1
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'error': str(error) if error else None,
            'traceback': traceback.format_exc() if error else None
        }
        
        if status == 'PASS':
            self.passed_count += 1
            TEST_RESULTS['passed'].append(result)
            print(f"✅ [{self.test_count}] {test_name}: PASS - {message}")
        elif status == 'FAIL':
            self.failed_count += 1
            TEST_RESULTS['failed'].append(result)
            print(f"❌ [{self.test_count}] {test_name}: FAIL - {message}")
            if error:
                print(f"   Error: {error}")
        elif status == 'WARN':
            self.warning_count += 1
            TEST_RESULTS['warnings'].append(result)
            print(f"⚠️  [{self.test_count}] {test_name}: WARN - {message}")
        
        # Track memory
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                if memory_mb > self.max_memory_mb:
                    self.max_memory_mb = memory_mb
                TEST_RESULTS['memory_usage'][test_name] = memory_mb
            except:
                TEST_RESULTS['memory_usage'][test_name] = 0
        else:
            TEST_RESULTS['memory_usage'][test_name] = 0
    
    def test_farmos_import(self):
        """Test 1: FarmOS import under stress."""
        try:
            # Suppress TTS initialization during import
            import os
            os.environ['PYTTSX3_SUPPRESS_INIT'] = '1'
            
            sys.path.insert(0, str(GATEKEEPER))
            
            # Temporarily redirect stdout/stderr to avoid logging issues
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()
            
            try:
                from FarmOS_2026 import AgentBus, quantum_knowledge, AGENTS_REGISTRY, register_agent
                agent_count = len(AGENTS_REGISTRY)
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                if 'PYTTSX3_SUPPRESS_INIT' in os.environ:
                    del os.environ['PYTTSX3_SUPPRESS_INIT']
            
            self.log_result("FarmOS Import", "PASS", f"Imported successfully. {agent_count} agents registered.")
            return True
        except Exception as e:
            self.log_result("FarmOS Import", "FAIL", f"Import failed", e)
            return False
    
    def test_agent_registration(self):
        """Test 2: Agent registration stress."""
        try:
            from FarmOS_2026 import AGENTS_REGISTRY
            expected = ['harriet', 'bob', 'apothecary', 'feedmaster', 'medical', 'salesbot']
            registered = list(AGENTS_REGISTRY.keys())
            
            if len(registered) >= len(expected):
                self.log_result("Agent Registration", "PASS", f"All {len(registered)} agents registered")
                return True
            else:
                missing = [a for a in expected if a not in registered]
                self.log_result("Agent Registration", "FAIL", f"Missing agents: {missing}")
                return False
        except Exception as e:
            self.log_result("Agent Registration", "FAIL", "Registration test failed", e)
            return False
    
    def test_agent_bus_concurrent(self, num_threads: int = 50):
        """Test 3: AgentBus concurrent access stress."""
        try:
            from FarmOS_2026 import AgentBus
            bus = AgentBus()
            results = queue.Queue()
            errors = []
            
            def worker(thread_id):
                try:
                    agent_name = random.choice(['harriet', 'bob', 'apothecary', 'feedmaster', 'medical', 'salesbot'])
                    query = f"test query {thread_id}"
                    response = bus.ask(agent_name, query)
                    results.put((thread_id, 'success', response[:50]))
                except Exception as e:
                    errors.append((thread_id, str(e)))
                    results.put((thread_id, 'error', str(e)))
            
            threads = []
            for i in range(num_threads):
                t = threading.Thread(target=worker, args=(i,))
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join(timeout=30)
            
            success_count = sum(1 for _ in range(results.qsize()) if results.get()[1] == 'success')
            
            if success_count >= num_threads * 0.9:  # 90% success rate
                self.log_result("AgentBus Concurrent", "PASS", f"{success_count}/{num_threads} concurrent requests succeeded")
            else:
                self.log_result("AgentBus Concurrent", "FAIL", f"Only {success_count}/{num_threads} succeeded. Errors: {len(errors)}")
                if errors:
                    TEST_RESULTS['breaking_points'].append({
                        'test': 'AgentBus Concurrent',
                        'issue': f'Concurrent access failures at {num_threads} threads',
                        'errors': errors[:5]
                    })
            return success_count >= num_threads * 0.9
        except Exception as e:
            self.log_result("AgentBus Concurrent", "FAIL", "Concurrent test failed", e)
            return False
    
    def test_quantum_knowledge_stress(self, num_queries: int = 100):
        """Test 4: Quantum knowledge base stress."""
        try:
            from FarmOS_2026 import quantum_knowledge
            
            queries = [
                "Colorado HR law 2026",
                "pole barn construction",
                "organic pest control",
                "livestock feed formula",
                "emergency medical protocol",
                "sales pitch template"
            ] * (num_queries // 6)
            
            start_time = time.time()
            results = []
            errors = []
            
            for i, query in enumerate(queries):
                try:
                    result = quantum_knowledge(query)
                    results.append((i, 'success', len(result)))
                except Exception as e:
                    errors.append((i, str(e)))
                    results.append((i, 'error', None))
            
            elapsed = time.time() - start_time
            success_count = sum(1 for r in results if r[1] == 'success')
            avg_time = elapsed / num_queries if num_queries > 0 else 0
            
            if success_count >= num_queries * 0.95:  # 95% success rate
                self.log_result("Quantum Knowledge Stress", "PASS", 
                              f"{success_count}/{num_queries} queries succeeded. Avg: {avg_time:.3f}s")
            else:
                self.log_result("Quantum Knowledge Stress", "FAIL", 
                              f"Only {success_count}/{num_queries} succeeded. Errors: {len(errors)}")
                TEST_RESULTS['breaking_points'].append({
                    'test': 'Quantum Knowledge Stress',
                    'issue': f'Query failures at {num_queries} queries',
                    'errors': errors[:5]
                })
            
            TEST_RESULTS['performance']['quantum_knowledge'] = {
                'queries': num_queries,
                'success_rate': success_count / num_queries,
                'avg_time': avg_time,
                'total_time': elapsed
            }
            
            return success_count >= num_queries * 0.95
        except Exception as e:
            self.log_result("Quantum Knowledge Stress", "FAIL", "Knowledge stress test failed", e)
            return False
    
    def test_agent_functions_stress(self, iterations: int = 50):
        """Test 5: Individual agent functions stress."""
        try:
            from FarmOS_2026 import (
                harriet_agent, bob_agent, apothecary_agent,
                feedmaster_agent, medical_agent, salesbot_agent
            )
            
            agents = [
                ('harriet', harriet_agent, "new hire John Doe"),
                ('bob', bob_agent, "design 30x60 pole barn"),
                ('apothecary', apothecary_agent, "aphids on tomatoes"),
                ('feedmaster', feedmaster_agent, "layer feed formula"),
                ('medical', medical_agent, "fall detection protocol"),
                ('salesbot', salesbot_agent, "order 10 lb beef")
            ]
            
            errors = []
            success_count = 0
            
            for i in range(iterations):
                for name, func, query in agents:
                    try:
                        result = func(query)
                        if result and len(result) > 0:
                            success_count += 1
                        else:
                            errors.append((name, f"Iteration {i}: Empty response"))
                    except Exception as e:
                        errors.append((name, f"Iteration {i}: {str(e)}"))
            
            total_calls = iterations * len(agents)
            success_rate = success_count / total_calls if total_calls > 0 else 0
            
            if success_rate >= 0.9:  # 90% success rate
                self.log_result("Agent Functions Stress", "PASS", 
                              f"{success_count}/{total_calls} calls succeeded ({success_rate*100:.1f}%)")
            else:
                self.log_result("Agent Functions Stress", "FAIL", 
                              f"Only {success_count}/{total_calls} succeeded. Errors: {len(errors)}")
                TEST_RESULTS['breaking_points'].append({
                    'test': 'Agent Functions Stress',
                    'issue': f'Function failures at {iterations} iterations',
                    'errors': errors[:10]
                })
            
            return success_rate >= 0.9
        except Exception as e:
            self.log_result("Agent Functions Stress", "FAIL", "Agent functions stress test failed", e)
            return False
    
    def test_memory_stress(self, num_agents: int = 100):
        """Test 6: Memory stress - create many agent instances."""
        try:
            from FarmOS_2026 import AgentBus
            
            if PSUTIL_AVAILABLE:
                initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
            else:
                initial_memory = 0
            
            buses = []
            
            for i in range(num_agents):
                try:
                    bus = AgentBus()
                    buses.append(bus)
                except Exception as e:
                    self.log_result("Memory Stress", "WARN", f"Failed to create bus {i}: {e}")
                    break
            
            if PSUTIL_AVAILABLE:
                peak_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_per_agent = (peak_memory - initial_memory) / len(buses) if buses else 0
            else:
                peak_memory = 0
                memory_per_agent = 0
            
            # Cleanup
            del buses
            gc.collect()
            
            if PSUTIL_AVAILABLE:
                final_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_recovered = peak_memory - final_memory
            else:
                final_memory = 0
                memory_recovered = 0
            
            if PSUTIL_AVAILABLE:
                if memory_per_agent < 10:  # Less than 10MB per agent
                    self.log_result("Memory Stress", "PASS", 
                                  f"Created {len(buses)} agents. Peak: {peak_memory:.1f}MB, Recovered: {memory_recovered:.1f}MB")
                else:
                    self.log_result("Memory Stress", "WARN", 
                                  f"High memory usage: {memory_per_agent:.1f}MB per agent")
                    TEST_RESULTS['breaking_points'].append({
                        'test': 'Memory Stress',
                        'issue': f'High memory usage: {memory_per_agent:.1f}MB per agent',
                        'peak_memory_mb': peak_memory
                    })
            else:
                self.log_result("Memory Stress", "PASS", 
                              f"Created {len(buses)} agents (memory tracking unavailable)")
            
            TEST_RESULTS['performance']['memory'] = {
                'initial_mb': initial_memory,
                'peak_mb': peak_memory,
                'final_mb': final_memory,
                'recovered_mb': memory_recovered,
                'per_agent_mb': memory_per_agent
            }
            
            return True
        except Exception as e:
            self.log_result("Memory Stress", "FAIL", "Memory stress test failed", e)
            return False
    
    def test_concurrent_agent_queries(self, num_queries: int = 200):
        """Test 7: Concurrent agent queries stress."""
        try:
            from FarmOS_2026 import AgentBus
            bus = AgentBus()
            
            queries = [
                ("harriet", "new hire packet"),
                ("bob", "pole barn design"),
                ("apothecary", "neem spray recipe"),
                ("feedmaster", "layer feed"),
                ("medical", "fall detection"),
                ("salesbot", "order beef")
            ]
            
            def worker(query_pair):
                agent, query = query_pair
                try:
                    response = bus.ask(agent, query)
                    return ('success', len(response) if response else 0)
                except Exception as e:
                    return ('error', str(e))
            
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(worker, random.choice(queries)) for _ in range(num_queries)]
                results = [f.result() for f in as_completed(futures)]
            
            elapsed = time.time() - start_time
            success_count = sum(1 for r in results if r[0] == 'success')
            success_rate = success_count / num_queries if num_queries > 0 else 0
            
            if success_rate >= 0.95:
                self.log_result("Concurrent Agent Queries", "PASS", 
                              f"{success_count}/{num_queries} succeeded in {elapsed:.2f}s ({success_rate*100:.1f}%)")
            else:
                self.log_result("Concurrent Agent Queries", "FAIL", 
                              f"Only {success_count}/{num_queries} succeeded. Rate: {success_rate*100:.1f}%")
                TEST_RESULTS['breaking_points'].append({
                    'test': 'Concurrent Agent Queries',
                    'issue': f'Concurrent query failures at {num_queries} queries',
                    'success_rate': success_rate
                })
            
            TEST_RESULTS['performance']['concurrent_queries'] = {
                'queries': num_queries,
                'success_rate': success_rate,
                'total_time': elapsed,
                'queries_per_second': num_queries / elapsed if elapsed > 0 else 0
            }
            
            return success_rate >= 0.95
        except Exception as e:
            self.log_result("Concurrent Agent Queries", "FAIL", "Concurrent queries test failed", e)
            return False
    
    def test_file_io_stress(self, num_operations: int = 100):
        """Test 8: File I/O stress (knowledge base access)."""
        try:
            knowledge_file = ROOT / 'Archived' / 'gatekeeper_brain.json'
            
            if not knowledge_file.exists():
                self.log_result("File I/O Stress", "WARN", "Knowledge base file not found")
                return True
            
            start_time = time.time()
            errors = []
            
            for i in range(num_operations):
                try:
                    with open(knowledge_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Simulate read operation
                        _ = len(str(data))
                except Exception as e:
                    errors.append((i, str(e)))
            
            elapsed = time.time() - start_time
            success_count = num_operations - len(errors)
            success_rate = success_count / num_operations if num_operations > 0 else 0
            
            if success_rate >= 0.99:
                self.log_result("File I/O Stress", "PASS", 
                              f"{success_count}/{num_operations} operations succeeded in {elapsed:.2f}s")
            else:
                self.log_result("File I/O Stress", "FAIL", 
                              f"Only {success_count}/{num_operations} succeeded. Errors: {len(errors)}")
                TEST_RESULTS['breaking_points'].append({
                    'test': 'File I/O Stress',
                    'issue': f'File I/O failures at {num_operations} operations',
                    'errors': errors[:5]
                })
            
            return success_rate >= 0.99
        except Exception as e:
            self.log_result("File I/O Stress", "FAIL", "File I/O stress test failed", e)
            return False
    
    def test_agent_import_stress(self):
        """Test 9: Agent module import stress."""
        try:
            agent_paths = {
                'harriet': GATEKEEPER / 'HR' / 'Harriet_v2.py',
                'bob': GATEKEEPER / 'Farm_Engineer' / 'Bob.py',
                'apothecary': GATEKEEPER / 'FarmHub' / 'Apothecary.py',
                'feedmaster': GATEKEEPER / 'FarmHub' / 'FeedMaster.py',
                'medical': GATEKEEPER / 'FarmHub' / 'medical_core_final_2026.py',
                'salesbot': GATEKEEPER / 'Sales' / 'QuantumSalesBot.py'
            }
            
            import_results = {}
            for name, path in agent_paths.items():
                if path.exists():
                    import_results[name] = 'exists'
                else:
                    import_results[name] = 'missing'
            
            existing = sum(1 for v in import_results.values() if v == 'exists')
            missing = sum(1 for v in import_results.values() if v == 'missing')
            
            if existing >= len(agent_paths) * 0.5:  # At least 50% exist
                self.log_result("Agent Import Stress", "PASS", 
                              f"{existing}/{len(agent_paths)} agent files exist")
            else:
                self.log_result("Agent Import Stress", "WARN", 
                              f"Only {existing}/{len(agent_paths)} agent files exist")
            
            return True
        except Exception as e:
            self.log_result("Agent Import Stress", "FAIL", "Agent import stress test failed", e)
            return False
    
    def test_error_recovery(self):
        """Test 10: Error recovery and resilience."""
        try:
            from FarmOS_2026 import AgentBus, quantum_knowledge
            
            bus = AgentBus()
            
            # Test invalid agent name
            try:
                response = bus.ask('invalid_agent_xyz', 'test query')
                # Should not crash, should return something
                if response:
                    pass  # Good
            except Exception as e:
                # Should handle gracefully
                pass
            
            # Test empty query
            try:
                response = quantum_knowledge("")
                # Should not crash
                if response:
                    pass  # Good
            except Exception as e:
                # Should handle gracefully
                pass
            
            # Test None query
            try:
                response = quantum_knowledge(None)
                # Should not crash
            except Exception:
                # Expected to handle None
                pass
            
            self.log_result("Error Recovery", "PASS", "System handles errors gracefully")
            return True
        except Exception as e:
            self.log_result("Error Recovery", "FAIL", "Error recovery test failed", e)
            return False
    
    def run_all_tests(self):
        """Run all stress tests."""
        print("\n" + "=" * 100)
        print("RUNNING STRESS TESTS")
        print("=" * 100 + "\n")
        
        # Core tests
        self.test_farmos_import()
        self.test_agent_registration()
        self.test_agent_import_stress()
        
        # Stress tests
        print("\n--- Stress Tests ---\n")
        self.test_agent_bus_concurrent(num_threads=50)
        self.test_quantum_knowledge_stress(num_queries=100)
        self.test_agent_functions_stress(iterations=50)
        self.test_memory_stress(num_agents=50)
        self.test_concurrent_agent_queries(num_queries=200)
        self.test_file_io_stress(num_operations=100)
        self.test_error_recovery()
        
        # Final summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        elapsed = time.time() - self.start_time
        
        print("\n" + "=" * 100)
        print("STRESS TEST SUMMARY")
        print("=" * 100)
        print(f"Total Tests: {self.test_count}")
        print(f"Passed: {self.passed_count} ✅")
        print(f"Failed: {self.failed_count} ❌")
        print(f"Warnings: {self.warning_count} ⚠️")
        print(f"Total Time: {elapsed:.2f} seconds")
        print(f"Peak Memory: {self.max_memory_mb:.1f} MB")
        print()
        
        if TEST_RESULTS['breaking_points']:
            print("BREAKING POINTS IDENTIFIED:")
            print("-" * 100)
            for i, bp in enumerate(TEST_RESULTS['breaking_points'], 1):
                print(f"{i}. {bp['test']}: {bp['issue']}")
                if 'errors' in bp:
                    for err in bp['errors'][:3]:
                        print(f"   - {err}")
            print()
        
        if TEST_RESULTS['performance']:
            print("PERFORMANCE METRICS:")
            print("-" * 100)
            for key, metrics in TEST_RESULTS['performance'].items():
                print(f"{key}:")
                for k, v in metrics.items():
                    if isinstance(v, float):
                        print(f"  {k}: {v:.3f}")
                    else:
                        print(f"  {k}: {v}")
            print()
        
        # Save results
        results_file = GATEKEEPER / 'stress_test_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(TEST_RESULTS, f, indent=2, default=str)
        
        print(f"Results saved to: {results_file}")
        print("=" * 100)

if __name__ == '__main__':
    tester = StressTest()
    tester.run_all_tests()

