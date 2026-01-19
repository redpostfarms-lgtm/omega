"""
Omega Unified Launcher
Launch any Omega tool or integrated utility from one place
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional

class OmegaLauncher:
    """
    Unified launcher for all Omega tools
    """

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_python = self.project_root / ".venv" / "Scripts" / "python.exe"

        self.tools = {
            'chatbot': 'omega_intelligent_chatbot.py',
            'monitor': 'omega_continuous_monitor.py',
            'optimizer': 'omega_quantum_idle_optimizer.py',
            'deep-dive': 'omega_deep_dive.py',
            'scanner': 'omega_package_scanner.py',

            'ai-extras': 'omega_ai_extras.py',
            'dev-tools': 'omega_dev_tools.py',
            'web-researcher': 'omega_web_researcher.py',
            'education': 'omega_education_system.py',

            'gradio': ['gradio', '--help'],
            'streamlit': ['streamlit', '--help'],
            'jupyter': ['jupyter', 'lab'],
            'pytest': ['pytest', '.'],
            'black': ['black', '.'],
            'flake8': ['flake8', '.']
        }

    def list_tools(self):
        """List all available tools"""
        print("\n" + "="*60)
        print("OMEGA UNIFIED LAUNCHER - AVAILABLE TOOLS")
        print("="*60)

        print("\nMain Systems:")
        main_tools = ['chatbot', 'monitor', 'optimizer', 'deep-dive', 'scanner']
        for tool in main_tools:
            print(f"  - {tool}")

        print("\nExtras:")
        extra_tools = ['ai-extras', 'dev-tools', 'web-researcher', 'education']
        for tool in extra_tools:
            print(f"  - {tool}")

        print("\nCLI Tools:")
        cli_tools = ['gradio', 'streamlit', 'jupyter', 'pytest', 'black', 'flake8']
        for tool in cli_tools:
            print(f"  - {tool}")

        print("\n" + "="*60)
        print("Usage: python omega_launcher.py <tool-name>")
        print("Example: python omega_launcher.py chatbot")
        print("="*60 + "\n")

    def launch(self, tool_name: str, *args):
        """Launch a tool"""
        if tool_name not in self.tools:
            print(f"[!] Tool '{tool_name}' not found")
            print("[*] Run 'python omega_launcher.py --list' to see available tools")
            return False

        tool_spec = self.tools[tool_name]

        if isinstance(tool_spec, str):
            script_path = self.project_root / tool_spec
            if script_path.exists():
                print(f"[*] Launching {tool_name}...")
                subprocess.run([str(self.venv_python), str(script_path)] + list(args))
                return True
            else:
                print(f"[!] Script not found: {tool_spec}")
                return False

        elif isinstance(tool_spec, list):
            print(f"[*] Running {tool_name}...")
            try:
                subprocess.run(tool_spec + list(args))
                return True
            except FileNotFoundError:
                print(f"[!] CLI tool '{tool_spec[0]}' not found")
                print("[*] Make sure it's installed and in PATH")
                return False

        return False

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Omega Unified Launcher')
    parser.add_argument('tool', nargs='?', help='Tool to launch')
    parser.add_argument('--list', action='store_true', help='List all tools')
    parser.add_argument('args', nargs='*', help='Tool arguments')

    args = parser.parse_args()

    launcher = OmegaLauncher()

    if args.list or not args.tool:
        launcher.list_tools()
    else:
        launcher.launch(args.tool, *args.args)

if __name__ == '__main__':
    main()
