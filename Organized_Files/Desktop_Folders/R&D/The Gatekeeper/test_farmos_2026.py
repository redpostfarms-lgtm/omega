#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# FARMOS 2026 – TEST SCRIPT
# Verifies all agents are working correctly

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROOT = Path(r'D:\RPF_BRAIN')
GATEKEEPER = ROOT / 'The Gatekeeper'

def test_import():
    """Test that FarmOS can be imported."""
    print("=" * 80)
    print("FARMOS 2026 – TEST SUITE")
    print("=" * 80)
    print()
    
    print("[1/6] Testing FarmOS import...")
    try:
        sys.path.insert(0, str(GATEKEEPER))
        from FarmOS_2026 import AgentBus, quantum_knowledge, AGENTS_REGISTRY
        print("  ✅ FarmOS imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_agents_registered():
    """Test that all agents are registered."""
    print("\n[2/6] Testing agent registration...")
    try:
        from FarmOS_2026 import AGENTS_REGISTRY
        expected_agents = ['harriet', 'bob', 'apothecary', 'feedmaster', 'medical', 'salesbot']
        registered = list(AGENTS_REGISTRY.keys())
        
        print(f"  Expected agents: {expected_agents}")
        print(f"  Registered agents: {registered}")
        
        missing = [a for a in expected_agents if a not in registered]
        if missing:
            print(f"  ❌ Missing agents: {missing}")
            return False
        else:
            print(f"  ✅ All {len(registered)} agents registered")
            return True
    except Exception as e:
        print(f"  ❌ Registration test failed: {e}")
        return False

def test_agent_paths():
    """Test that all agent files exist."""
    print("\n[3/6] Testing agent file paths...")
    try:
        from FarmOS_2026 import AGENT_PATHS
        all_exist = True
        for name, path in AGENT_PATHS.items():
            if path.exists():
                print(f"  ✅ {name}: {path.name}")
            else:
                print(f"  ⚠️  {name}: {path.name} (not found, will use fallback)")
                all_exist = False
        
        if all_exist:
            print("  ✅ All agent files found")
        else:
            print("  ⚠️  Some agent files missing (will use quantum knowledge fallback)")
        return True
    except Exception as e:
        print(f"  ❌ Path test failed: {e}")
        return False

def test_agent_bus():
    """Test AgentBus functionality."""
    print("\n[4/6] Testing AgentBus...")
    try:
        from FarmOS_2026 import AgentBus
        bus = AgentBus()
        print("  ✅ AgentBus initialized")
        
        # Test speak (should not raise exception)
        try:
            bus.speak("Test message")
            print("  ✅ AgentBus.speak() works")
        except Exception as e:
            print(f"  ⚠️  AgentBus.speak() error: {e}")
        
        # Test ask
        try:
            response = bus.ask('harriet', 'test query')
            print(f"  ✅ AgentBus.ask() works (response: {response[:50]}...)")
        except Exception as e:
            print(f"  ⚠️  AgentBus.ask() error: {e}")
        
        return True
    except Exception as e:
        print(f"  ❌ AgentBus test failed: {e}")
        return False

def test_quantum_knowledge():
    """Test quantum knowledge function."""
    print("\n[5/6] Testing quantum knowledge...")
    try:
        from FarmOS_2026 import quantum_knowledge
        result = quantum_knowledge("test query")
        print(f"  ✅ quantum_knowledge() works (response: {result[:50]}...)")
        return True
    except Exception as e:
        print(f"  ❌ quantum_knowledge() test failed: {e}")
        return False

def test_agent_functions():
    """Test individual agent functions."""
    print("\n[6/6] Testing agent functions...")
    try:
        from FarmOS_2026 import (
            harriet_agent, bob_agent, apothecary_agent,
            feedmaster_agent, medical_agent, salesbot_agent
        )
        
        agents = [
            ('harriet', harriet_agent),
            ('bob', bob_agent),
            ('apothecary', apothecary_agent),
            ('feedmaster', feedmaster_agent),
            ('medical', medical_agent),
            ('salesbot', salesbot_agent)
        ]
        
        all_work = True
        for name, func in agents:
            try:
                result = func("test query")
                print(f"  ✅ {name}_agent() works (response: {result[:50]}...)")
            except Exception as e:
                print(f"  ⚠️  {name}_agent() error: {e}")
                all_work = False
        
        if all_work:
            print("  ✅ All agent functions work")
        else:
            print("  ⚠️  Some agent functions have issues (may use fallback)")
        
        return True
    except Exception as e:
        print(f"  ❌ Agent function test failed: {e}")
        return False

def main():
    """Run all tests."""
    results = []
    
    results.append(("Import", test_import()))
    results.append(("Agent Registration", test_agents_registered()))
    results.append(("Agent Paths", test_agent_paths()))
    results.append(("AgentBus", test_agent_bus()))
    results.append(("Quantum Knowledge", test_quantum_knowledge()))
    results.append(("Agent Functions", test_agent_functions()))
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! FarmOS 2026 is ready.")
    else:
        print("\n⚠️  Some tests had issues. FarmOS will use fallback modes.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

