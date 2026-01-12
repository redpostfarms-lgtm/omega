#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# OMEGA COMPREHENSIVE TEST
# Tests all Phase 1 and Phase 2 systems

import json
import time
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('Omega.Test')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'

def test_phase1():
    """Test Phase 1 systems."""
    print("\n" + "=" * 60)
    print("PHASE 1 TESTING")
    print("=" * 60)
    
    results = {"vector_rag": False, "multimodal": False, "integration": False}
    
    # Test Vector RAG
    try:
        from omega_vector_rag_system import OmegaVectorRAG
        rag = OmegaVectorRAG()
        
        # Index test document
        doc_id = rag.index_document(
            "Omega is a quantum-enhanced AI system with multi-LLM fusion.",
            {"source": "test", "type": "system"}
        )
        
        # Search
        search_results = rag.search("What is Omega?", top_k=3)
        
        if search_results and search_results['count'] > 0:
            results["vector_rag"] = True
            print("✅ Vector RAG: PASSED")
            print(f"   - Indexed document: {doc_id}")
            print(f"   - Found {search_results['count']} results")
        else:
            print("❌ Vector RAG: FAILED - No search results")
    except Exception as e:
        print(f"❌ Vector RAG: FAILED - {e}")
    
    # Test Multi-Modal
    try:
        from omega_multimodal_processor import OmegaMultiModalProcessor
        processor = OmegaMultiModalProcessor()
        
        capabilities = processor.get_capabilities()
        if capabilities:
            results["multimodal"] = True
            print("✅ Multi-Modal: PASSED")
            print(f"   - Vision: {capabilities.get('vision', False)}")
            print(f"   - Audio: {capabilities.get('audio', False)}")
            print(f"   - Video: {capabilities.get('video', False)}")
        else:
            print("❌ Multi-Modal: FAILED")
    except Exception as e:
        print(f"❌ Multi-Modal: FAILED - {e}")
    
    # Test Phase 1 Integration
    try:
        from omega_phase1_integration import OmegaPhase1Integration
        integration = OmegaPhase1Integration()
        
        status = integration.get_status()
        if status:
            results["integration"] = True
            print("✅ Phase 1 Integration: PASSED")
            print(f"   - Vector RAG: {status['vector_rag']['available']}")
            print(f"   - Multi-Modal: {status['multimodal']['available']}")
        else:
            print("❌ Phase 1 Integration: FAILED")
    except Exception as e:
        print(f"❌ Phase 1 Integration: FAILED - {e}")
    
    return results

def test_phase2():
    """Test Phase 2 systems."""
    print("\n" + "=" * 60)
    print("PHASE 2 TESTING")
    print("=" * 60)
    
    results = {"quantum_ml": False, "autonomous_agent": False, "code_sandbox": False, "integration": False}
    
    # Test Quantum ML
    try:
        from omega_quantum_ml import QuantumMLPipeline
        pipeline = QuantumMLPipeline()
        
        capabilities = pipeline.get_capabilities()
        if capabilities is not None:
            results["quantum_ml"] = True
            print("✅ Quantum ML: PASSED")
            print(f"   - Quantum ML: {capabilities.get('quantum_ml', False)}")
            print(f"   - Hybrid Models: {capabilities.get('hybrid_models', False)}")
        else:
            print("❌ Quantum ML: FAILED")
    except Exception as e:
        print(f"❌ Quantum ML: FAILED - {e}")
    
    # Test Autonomous Agent
    try:
        from omega_autonomous_agent import AgentFramework
        framework = AgentFramework()
        
        agent = framework.create_agent("test_agent", "TestAgent")
        goal = agent.set_goal("Test goal for comprehensive testing")
        
        if goal and len(goal.tasks) > 0:
            results["autonomous_agent"] = True
            print("✅ Autonomous Agent: PASSED")
            print(f"   - Goal created: {goal.id}")
            print(f"   - Tasks: {len(goal.tasks)}")
        else:
            print("❌ Autonomous Agent: FAILED")
    except Exception as e:
        print(f"❌ Autonomous Agent: FAILED - {e}")
    
    # Test Code Sandbox
    try:
        from omega_code_sandbox import CodeSandbox
        sandbox = CodeSandbox()
        
        # Test safe code
        result = sandbox.execute("result = 5 * 10\nprint(f'Result: {result}')")
        
        if result.success and "Result: 50" in result.output:
            results["code_sandbox"] = True
            print("✅ Code Sandbox: PASSED")
            print(f"   - Safe code execution: OK")
            
            # Test security
            dangerous_result = sandbox.execute("import os")
            if not dangerous_result.success:
                print(f"   - Security check: OK")
        else:
            print("❌ Code Sandbox: FAILED")
    except Exception as e:
        print(f"❌ Code Sandbox: FAILED - {e}")
    
    # Test Phase 2 Integration
    try:
        from omega_phase2_integration import OmegaPhase2Integration
        integration = OmegaPhase2Integration()
        
        status = integration.get_status()
        if status:
            results["integration"] = True
            print("✅ Phase 2 Integration: PASSED")
            print(f"   - Quantum ML: {status['quantum_ml']['available']}")
            print(f"   - Agent Framework: {status['agent_framework']['available']}")
            print(f"   - Code Sandbox: {status['code_sandbox']['available']}")
        else:
            print("❌ Phase 2 Integration: FAILED")
    except Exception as e:
        print(f"❌ Phase 2 Integration: FAILED - {e}")
    
    return results

def test_integration():
    """Test cross-phase integration."""
    print("\n" + "=" * 60)
    print("CROSS-PHASE INTEGRATION TESTING")
    print("=" * 60)
    
    results = {"phase1_phase2": False}
    
    try:
        from omega_phase1_integration import OmegaPhase1Integration
        from omega_phase2_integration import OmegaPhase2Integration
        
        phase1 = OmegaPhase1Integration()
        phase2 = OmegaPhase2Integration()
        
        # Test: Agent using RAG
        if phase1.vector_rag and phase2.agent_framework:
            # Index document
            doc_id = phase1.index_document("Omega systems are fully integrated.", {"source": "integration_test"})
            
            # Create agent
            agent = phase2.create_agent("integration_agent", "IntegrationAgent")
            
            # Search knowledge
            search_results = phase1.search_knowledge("Omega systems", top_k=1)
            
            if search_results and search_results['count'] > 0:
                results["phase1_phase2"] = True
                print("✅ Phase 1 + Phase 2 Integration: PASSED")
                print(f"   - Agent created: {agent.name}")
                print(f"   - RAG search: {search_results['count']} results")
            else:
                print("❌ Phase 1 + Phase 2 Integration: FAILED")
        else:
            print("⚠️  Phase 1 + Phase 2 Integration: SKIPPED (dependencies not available)")
    except Exception as e:
        print(f"❌ Phase 1 + Phase 2 Integration: FAILED - {e}")
    
    return results

def main():
    """Run comprehensive tests."""
    print("=" * 60)
    print("OMEGA COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"Test started: {datetime.now().isoformat()}")
    
    start_time = time.time()
    
    # Test Phase 1
    phase1_results = test_phase1()
    
    # Test Phase 2
    phase2_results = test_phase2()
    
    # Test Integration
    integration_results = test_integration()
    
    # Summary
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    print("\nPhase 1 Results:")
    phase1_passed = sum(1 for v in phase1_results.values() if v)
    phase1_total = len(phase1_results)
    print(f"  Passed: {phase1_passed}/{phase1_total}")
    for test, passed in phase1_results.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {test}")
    
    print("\nPhase 2 Results:")
    phase2_passed = sum(1 for v in phase2_results.values() if v)
    phase2_total = len(phase2_results)
    print(f"  Passed: {phase2_passed}/{phase2_total}")
    for test, passed in phase2_results.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {test}")
    
    print("\nIntegration Results:")
    integration_passed = sum(1 for v in integration_results.values() if v)
    integration_total = len(integration_results)
    print(f"  Passed: {integration_passed}/{integration_total}")
    for test, passed in integration_results.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {test}")
    
    total_passed = phase1_passed + phase2_passed + integration_passed
    total_tests = phase1_total + phase2_total + integration_total
    
    print(f"\nOverall: {total_passed}/{total_tests} tests passed")
    print(f"Test duration: {elapsed_time:.2f} seconds")
    print(f"Test completed: {datetime.now().isoformat()}")
    
    print("\n" + "=" * 60)
    
    # Save results
    results_file = GATE / 'omega_test_results.json'
    results_data = {
        "timestamp": datetime.now().isoformat(),
        "phase1": phase1_results,
        "phase2": phase2_results,
        "integration": integration_results,
        "summary": {
            "phase1_passed": phase1_passed,
            "phase1_total": phase1_total,
            "phase2_passed": phase2_passed,
            "phase2_total": phase2_total,
            "integration_passed": integration_passed,
            "integration_total": integration_total,
            "total_passed": total_passed,
            "total_tests": total_tests,
            "elapsed_time": elapsed_time
        }
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"Results saved to: {results_file}")

if __name__ == "__main__":
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)
