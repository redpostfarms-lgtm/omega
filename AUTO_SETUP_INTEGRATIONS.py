#!/usr/bin/env python3
"""
Auto Setup Developer Integrations
==================================
Automated setup that opens browsers and guides through setup
"""

import sys
from pathlib import Path
from omega_developer_integrations import get_integration_manager, IntegrationStatus
import webbrowser

def main():
    """Automated setup process"""
    print("=" * 80)
    print("OMEGA DEVELOPER INTEGRATIONS - AUTOMATED SETUP")
    print("=" * 80)
    print()
    
    manager = get_integration_manager()
    
    # Get tools needing setup
    needs_setup = manager.get_tools_needing_setup()
    needs_human = manager.get_tools_needing_human()
    
    print(f"Found {len(needs_setup)} tools needing setup")
    print(f"Found {len(needs_human)} tools needing human interaction")
    print()
    
    # Priority order: Most useful tools first
    priority_tools = [
        "huggingface",  # Most versatile, free tier
        "nvidia_playground",  # GPU resources
        "replicate",  # Easy model access
        "google_colab",  # Free compute
        "kaggle",  # Datasets and compute
        "openai_free",  # GPT access
        "anthropic_free"  # Claude access
    ]
    
    print("=" * 80)
    print("SETTING UP PRIORITY TOOLS")
    print("=" * 80)
    print()
    
    tools_to_setup = []
    for tool_name in priority_tools:
        if tool_name in manager.tools:
            tool = manager.tools[tool_name]
            if tool.status != IntegrationStatus.COMPLETE:
                tools_to_setup.append(tool_name)
    
    print(f"Tools to set up: {len(tools_to_setup)}")
    for tool_name in tools_to_setup:
        tool = manager.tools[tool_name]
        print(f"  - {tool.name}")
    print()
    
    # Initiate setup for each tool
    setup_info = []
    for tool_name in tools_to_setup[:3]:  # Start with top 3
        tool = manager.tools[tool_name]
        print(f"\n{'='*80}")
        print(f"SETTING UP: {tool.name}")
        print(f"{'='*80}")
        print(f"URL: {tool.url}")
        print(f"Account Setup URL: {tool.account_setup_url}")
        print()
        print("SETUP INSTRUCTIONS:")
        print(tool.setup_instructions)
        print()
        
        # Open browser
        if tool.account_setup_url:
            print(f"Opening browser for {tool.name}...")
            try:
                webbrowser.open(tool.account_setup_url)
                setup_info.append({
                    "tool": tool_name,
                    "name": tool.name,
                    "url": tool.account_setup_url,
                    "instructions": tool.setup_instructions,
                    "needs_api_key": tool.requires_api_key
                })
                print(f"✅ Browser opened for {tool.name}")
                print(f"⏳ Please complete account setup, then run:")
                print(f"   python SETUP_DEVELOPER_INTEGRATIONS.py")
                print(f"   Choose option 2 to enter API key for '{tool_name}'")
            except Exception as e:
                print(f"❌ Could not open browser: {e}")
        
        print()
    
    # Save setup info
    setup_info_file = Path("developer_integrations") / "setup_info.json"
    import json
    with open(setup_info_file, 'w') as f:
        json.dump(setup_info, f, indent=2)
    
    print("=" * 80)
    print("SETUP INITIATED")
    print("=" * 80)
    print()
    print(f"✅ Opened {len(setup_info)} browser windows")
    print(f"📝 Setup instructions saved to: {setup_info_file}")
    print()
    print("NEXT STEPS:")
    print("1. Complete account setup in the opened browsers")
    print("2. Generate API keys from each service")
    print("3. Run: python SETUP_DEVELOPER_INTEGRATIONS.py")
    print("4. Choose option 2 to enter API keys")
    print()
    
    # Show current status
    report = manager.get_setup_report()
    print("=" * 80)
    print("CURRENT STATUS")
    print("=" * 80)
    print(f"Total Tools: {report['total_tools']}")
    print(f"Complete: {report['complete']} ✅")
    print(f"Needs Setup: {report['needs_setup']} ⏳")
    print(f"Needs Human: {report['needs_human']} 👤")
    print()

if __name__ == "__main__":
    main()
