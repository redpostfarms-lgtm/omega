#!/usr/bin/env python3
"""
Setup Developer Integrations
============================
Interactive setup for free developer tool integrations
"""

import sys
from pathlib import Path
from omega_developer_integrations import get_integration_manager, IntegrationStatus

def print_header():
    """Print header"""
    print("=" * 80)
    print("OMEGA DEVELOPER INTEGRATIONS SETUP")
    print("=" * 80)
    print()

def print_tool_info(tool):
    """Print tool information"""
    print(f"Name: {tool.name}")
    print(f"URL: {tool.url}")
    print(f"Free Tier: {'Yes' if tool.free_tier else 'No'}")
    print(f"Requires Account: {'Yes' if tool.requires_account else 'No'}")
    print(f"Requires API Key: {'Yes' if tool.requires_api_key else 'No'}")
    print(f"Status: {tool.status.value}")
    print()

def main():
    """Main setup function"""
    print_header()
    
    manager = get_integration_manager()
    
    # Show available tools
    print("Available Developer Tools:")
    print("-" * 80)
    for i, (name, tool) in enumerate(manager.tools.items(), 1):
        status_icon = "✅" if tool.status == IntegrationStatus.COMPLETE else "⏳"
        print(f"{i}. {status_icon} {tool.name} ({name})")
    print()
    
    # Show tools needing setup
    needs_setup = manager.get_tools_needing_setup()
    if needs_setup:
        print("Tools Needing Setup:")
        print("-" * 80)
        for i, tool in enumerate(needs_setup, 1):
            print(f"{i}. {tool.name}")
        print()
    
    # Show tools needing human interaction
    needs_human = manager.get_tools_needing_human()
    if needs_human:
        print("Tools Needing Human Interaction:")
        print("-" * 80)
        for i, tool in enumerate(needs_human, 1):
            print(f"{i}. {tool.name}")
            print(f"   Setup URL: {tool.account_setup_url}")
            print(f"   Instructions: {tool.setup_instructions[:100]}...")
        print()
    
    # Interactive setup
    print("=" * 80)
    print("INTERACTIVE SETUP")
    print("=" * 80)
    print()
    print("Options:")
    print("1. Initiate setup for a tool")
    print("2. Set API key for a tool")
    print("3. View setup status")
    print("4. Generate integration code")
    print("5. Exit")
    print()
    
    while True:
        try:
            choice = input("Enter option (1-5): ").strip()
            
            if choice == "1":
                # Initiate setup
                print("\nAvailable tools:")
                tools_list = list(manager.tools.items())
                for i, (name, tool) in enumerate(tools_list, 1):
                    print(f"{i}. {tool.name} ({name})")
                
                tool_choice = input("\nEnter tool number: ").strip()
                try:
                    tool_idx = int(tool_choice) - 1
                    if 0 <= tool_idx < len(tools_list):
                        tool_name = tools_list[tool_idx][0]
                        success, message = manager.initiate_setup(tool_name)
                        print(f"\n{message}\n")
                        if success and "Opened" in message:
                            api_key = input("Enter API key (or press Enter to skip): ").strip()
                            if api_key:
                                success, msg = manager.set_api_key(tool_name, api_key)
                                print(f"\n{msg}\n")
                    else:
                        print("Invalid tool number\n")
                except ValueError:
                    print("Invalid input\n")
            
            elif choice == "2":
                # Set API key
                print("\nTools with API key support:")
                api_tools = [(name, tool) for name, tool in manager.tools.items() 
                            if tool.requires_api_key]
                for i, (name, tool) in enumerate(api_tools, 1):
                    has_key = "✅" if tool.api_key else "❌"
                    print(f"{i}. {has_key} {tool.name} ({name})")
                
                tool_choice = input("\nEnter tool number: ").strip()
                try:
                    tool_idx = int(tool_choice) - 1
                    if 0 <= tool_idx < len(api_tools):
                        tool_name = api_tools[tool_idx][0]
                        api_key = input("Enter API key: ").strip()
                        if api_key:
                            success, message = manager.set_api_key(tool_name, api_key)
                            print(f"\n{message}\n")
                        else:
                            print("API key cannot be empty\n")
                    else:
                        print("Invalid tool number\n")
                except ValueError:
                    print("Invalid input\n")
            
            elif choice == "3":
                # View status
                report = manager.get_setup_report()
                print("\n" + "=" * 80)
                print("SETUP STATUS REPORT")
                print("=" * 80)
                print(f"Total Tools: {report['total_tools']}")
                print(f"Complete: {report['complete']}")
                print(f"Needs Human: {report['needs_human']}")
                print(f"Needs Setup: {report['needs_setup']}")
                print()
                print("Tool Status:")
                for name, info in report['tools'].items():
                    status_icon = "✅" if info['status'] == 'complete' else "⏳"
                    key_icon = "🔑" if info['has_api_key'] else "❌"
                    print(f"  {status_icon} {key_icon} {info['name']} ({name}): {info['status']}")
                print()
            
            elif choice == "4":
                # Generate integration code
                print("\nAvailable tools:")
                tools_list = list(manager.tools.items())
                for i, (name, tool) in enumerate(tools_list, 1):
                    print(f"{i}. {tool.name} ({name})")
                
                tool_choice = input("\nEnter tool number: ").strip()
                try:
                    tool_idx = int(tool_choice) - 1
                    if 0 <= tool_idx < len(tools_list):
                        tool_name = tools_list[tool_idx][0]
                        code = manager.generate_integration_code(tool_name)
                        print("\n" + "=" * 80)
                        print(f"INTEGRATION CODE FOR {tool_name.upper()}")
                        print("=" * 80)
                        print(code)
                        print("=" * 80)
                        print()
                    else:
                        print("Invalid tool number\n")
                except ValueError:
                    print("Invalid input\n")
            
            elif choice == "5":
                print("\nExiting setup. Configuration saved.")
                break
            
            else:
                print("Invalid option. Please enter 1-5.\n")
        
        except KeyboardInterrupt:
            print("\n\nExiting setup. Configuration saved.")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    main()
