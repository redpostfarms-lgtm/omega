#!/usr/bin/env python3
"""
Auto Tool Quick Launcher - Simple interface to auto tool management
Usage: python auto_tool_launcher.py [command] [args...]
"""

import sys
import os
import argparse
from pathlib import Path
import tempfile

# Import the managers
from auto_tool_manager import AutoToolManager
from tool_access_manager import (
    ToolAccessManager,
    SmartToolRouter,
    ensure_java,
    ensure_build_tool,
    run_build
)


class ToolLauncher:
    """User-friendly tool launcher interface"""
    
    def __init__(self):
        self.tool_manager = AutoToolManager()
        self.tool_manager.setup()
        
        self.access_manager = ToolAccessManager()
        self.router = SmartToolRouter(self.access_manager)
    
    def cmd_detect(self, args):
        """Detect all available tools"""
        print("\n=== Detecting Available Tools ===\n")
        self.tool_manager.detector.detect_all_tools()
        self.tool_manager.report()
    
    def cmd_ensure(self, args):
        """Ensure a specific tool is available"""
        if not args.tool:
            print("Error: --tool required")
            return
        
        print(f"\nEnsuring tool: {args.tool}")
        success = self.access_manager.access_tool(args.tool, auto_ensure=True)
        if success:
            print(f"✓ {args.tool} is ready at: {success}")
        else:
            print(f"✗ Failed to ensure {args.tool}")
    
    def cmd_project(self, args):
        """Ensure all tools for a project"""
        project_path = args.project or '.'
        print(f"\nEnsuring tools for project: {project_path}")
        
        tools = self.access_manager.access_tools_for_project(project_path)
        print(f"\n✓ Available tools:")
        for tool, path in tools.items():
            print(f"  {tool}: {path}")
    
    def cmd_build(self, args):
        """Auto-detect and build a project"""
        project_path = args.project or '.'
        print(f"\nBuilding project: {project_path}")
        
        result = run_build(project_path)
        if result and result.returncode == 0:
            print(f"\n✓ Build successful!")
        else:
            print(f"\n✗ Build failed!")
    
    def cmd_status(self, args):
        """Show tool status"""
        print("\n=== Tool Status ===\n")
        print("Cached Tools:")
        for tool, path in self.access_manager.tool_cache.items():
            print(f"  {tool}: {path}")
        
        print("\nTool Paths:")
        for tool, path in self.access_manager.tool_paths.items():
            print(f"  {tool}: {path}")
    
    def cmd_help(self, args):
        """Show help information"""
        help_text = """
=== Auto Tool Manager Commands ===

detect          Detect all available tools on system
ensure          Ensure a specific tool is available
  --tool NAME   Tool name (java, gradle, maven, python, etc.)

project         Ensure tools for a project
  --project DIR Project directory (default: current)

build           Auto-detect and build project
  --project DIR Project directory (default: current)

status          Show cached tool information

help            Show this help message

Examples:
  python auto_tool_launcher.py detect
  python auto_tool_launcher.py ensure --tool java
  python auto_tool_launcher.py project --project ./my-project
  python auto_tool_launcher.py build --project ./my-project
"""
        print(help_text)
    
    def run(self):
        """Run the launcher"""
        parser = argparse.ArgumentParser(
            description='Auto Tool Manager Launcher',
            add_help=False
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Command to run')
        
        # Detect command
        subparsers.add_parser('detect', help='Detect available tools')
        
        # Ensure command
        ensure_parser = subparsers.add_parser('ensure', help='Ensure tool availability')
        ensure_parser.add_argument('--tool', help='Tool name')
        
        # Project command
        project_parser = subparsers.add_parser('project', help='Ensure project tools')
        project_parser.add_argument('--project', help='Project directory')
        
        # Build command
        build_parser = subparsers.add_parser('build', help='Build project')
        build_parser.add_argument('--project', help='Project directory')
        
        # Status command
        subparsers.add_parser('status', help='Show tool status')
        
        # Help command
        subparsers.add_parser('help', help='Show help')
        
        args = parser.parse_args()
        
        if not args.command or args.command == 'help':
            self.cmd_help(args)
        elif args.command == 'detect':
            self.cmd_detect(args)
        elif args.command == 'ensure':
            self.cmd_ensure(args)
        elif args.command == 'project':
            self.cmd_project(args)
        elif args.command == 'build':
            self.cmd_build(args)
        elif args.command == 'status':
            self.cmd_status(args)
        else:
            self.cmd_help(args)


def main():
    launcher = ToolLauncher()
    launcher.run()


if __name__ == '__main__':
    main()
