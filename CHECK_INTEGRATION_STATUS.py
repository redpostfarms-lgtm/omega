#!/usr/bin/env python3
"""
Check Integration Status
========================
Non-interactive status display
"""

from omega_developer_integrations import get_integration_manager, IntegrationStatus

def main():
    manager = get_integration_manager()
    report = manager.get_setup_report()
    
    print("=" * 80)
    print("OMEGA DEVELOPER INTEGRATIONS - STATUS REPORT")
    print("=" * 80)
    print()
    print(f"Total Tools: {report['total_tools']}")
    print(f"Complete: {report['complete']} ✅")
    print(f"Needs Setup: {report['needs_setup']} ⏳")
    print(f"Needs Human: {report['needs_human']} 👤")
    print()
    print("=" * 80)
    print("TOOL STATUS")
    print("=" * 80)
    print()
    
    for name, info in report['tools'].items():
        status_icon = "✅" if info['status'] == 'complete' else "⏳" if info['status'] == 'in_progress' else "🔴"
        key_icon = "🔑" if info['has_api_key'] else "❌"
        tool = manager.tools[name]
        print(f"{status_icon} {key_icon} {info['name']}")
        print(f"   Status: {info['status']}")
        print(f"   URL: {tool.url}")
        if tool.account_setup_url:
            print(f"   Setup URL: {tool.account_setup_url}")
        print()
    
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("To set up tools:")
    print("1. Run: python SETUP_DEVELOPER_INTEGRATIONS.py")
    print("2. Choose option 1 to initiate setup")
    print("3. Complete account setup in browser")
    print("4. Choose option 2 to enter API keys")
    print()

if __name__ == "__main__":
    main()
