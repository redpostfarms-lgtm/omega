#!/usr/bin/env python3
"""
Run All Setup and Checks
========================
Runs all helpful optional scripts and checks automatically
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

def run_command(script_name, description):
    """Run a script and return status"""
    print(f"\n{'='*80}")
    print(f"RUNNING: {description}")
    print(f"Script: {script_name}")
    print('='*80)
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ {description} - COMPLETE")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"⚠️  {description} - COMPLETED WITH WARNINGS")
            if result.stderr:
                print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  {description} - TIMED OUT (took longer than 5 minutes)")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    print("="*80)
    print("OMEGA - COMPREHENSIVE SETUP AND CHECKS")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = {}
    
    # 1. Check integration status
    print("\n[1/6] Checking integration status...")
    try:
        from omega_developer_integrations import get_integration_manager
        manager = get_integration_manager()
        report = manager.get_setup_report()
        results['integrations'] = {
            'total': report['total_tools'],
            'complete': report['complete'],
            'needs_setup': report['needs_setup']
        }
        print(f"✅ Integrations: {report['complete']}/{report['total_tools']} complete")
    except Exception as e:
        print(f"⚠️  Integration check failed: {e}")
        results['integrations'] = {'error': str(e)}
    
    # 2. Run full integration scan
    print("\n[2/6] Running full integration scan...")
    results['scan'] = run_command('FULL_INTEGRATION_SCAN_AND_OPTIMIZATION.py', 
                                  'Full Integration Scan')
    
    # 3. Run code optimizer
    print("\n[3/6] Running code optimizer...")
    results['optimization'] = run_command('omega_code_optimizer.py',
                                         'Code Optimization')
    
    # 4. Run system audit
    print("\n[4/6] Running system audit...")
    if Path('omega_system_audit.py').exists():
        results['audit'] = run_command('omega_system_audit.py',
                                      'System Audit')
    else:
        print("⚠️  System audit script not found")
        results['audit'] = False
    
    # 5. Run test scripts (quick checks)
    print("\n[5/6] Running test scripts...")
    test_scripts = ['test_slang_processor.py', 'test_system.py']
    for test_script in test_scripts:
        if Path(test_script).exists():
            print(f"\nRunning {test_script}...")
            results[f'test_{test_script}'] = run_command(test_script,
                                                         f'Test: {test_script}')
    
    # 6. Setup integrations (open browsers)
    print("\n[6/6] Setting up developer integrations...")
    try:
        from omega_developer_integrations import get_integration_manager
        import webbrowser
        manager = get_integration_manager()
        priority_tools = ['huggingface', 'nvidia_playground', 'replicate']
        opened = 0
        for tool_name in priority_tools:
            if tool_name in manager.tools:
                tool = manager.tools[tool_name]
                if tool.account_setup_url and tool.status.value == 'not_started':
                    try:
                        webbrowser.open(tool.account_setup_url)
                        opened += 1
                        print(f"✅ Opened browser for: {tool.name}")
                    except:
                        pass
        if opened > 0:
            print(f"✅ Opened {opened} browser windows for account setup")
            results['integrations_setup'] = True
        else:
            print("ℹ️  No new integrations to set up")
            results['integrations_setup'] = False
    except Exception as e:
        print(f"⚠️  Integration setup failed: {e}")
        results['integrations_setup'] = False
    
    # Summary
    print("\n" + "="*80)
    print("SETUP AND CHECKS - SUMMARY")
    print("="*80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Results:")
    for key, value in results.items():
        if isinstance(value, dict):
            print(f"  {key}: {value}")
        else:
            status = "✅" if value else "❌"
            print(f"  {status} {key}: {'SUCCESS' if value else 'FAILED/SKIPPED'}")
    
    print("\n" + "="*80)
    print("SETUP COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("- Complete account setup in opened browser windows")
    print("- Enter API keys: python SETUP_DEVELOPER_INTEGRATIONS.py")
    print("- Review scan/audit results in generated reports")
    print()

if __name__ == "__main__":
    main()
