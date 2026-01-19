#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GATE IDE Integration
Integrates GATE with VS Code, PyCharm, and other IDEs
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")


class GateIDEIntegration:
    """IDE integration for GATE"""

    def __init__(self):
        self.root = Path(__file__).parent

    def setup_vscode(self):
        """Setup VS Code integration"""
        vscode_dir = self.root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)

        # Settings
        settings = {
            "python.defaultInterpreterPath": sys.executable,
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": False,
            "python.linting.flake8Enabled": False,
            "python.linting.ruffEnabled": True,
            "python.formatting.provider": "black",
            "python.testing.pytestEnabled": True,
            "python.testing.pytestArgs": ["tests"],
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": True
            },
            "files.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True,
                "**/.pytest_cache": True
            },
            "python.analysis.typeCheckingMode": "basic",
            "python.analysis.autoImportCompletions": True,
            "git.enableSmartCommit": True,
            "git.confirmSync": False
        }

        with open(vscode_dir / "settings.json", "w") as f:
            json.dump(settings, f, indent=4)

        # Launch configurations
        launch = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "GATE: Start Daemon",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/gate_daemon.py",
                    "console": "integratedTerminal"
                },
                {
                    "name": "GATE: Run Tests",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/run_comprehensive_tests.py",
                    "console": "integratedTerminal"
                },
                {
                    "name": "GATE: Control Center",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/setup_gate_admin.py",
                    "console": "integratedTerminal"
                }
            ]
        }

        with open(vscode_dir / "launch.json", "w") as f:
            json.dump(launch, f, indent=4)

        # Tasks
        tasks = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "GATE: Run Patrol",
                    "type": "shell",
                    "command": f"{sys.executable}",
                    "args": ["gate_autonomous_admin.py"],
                    "presentation": {
                        "reveal": "always",
                        "panel": "new"
                    }
                },
                {
                    "label": "GATE: Install Dependencies",
                    "type": "shell",
                    "command": f"{sys.executable}",
                    "args": ["gate_comprehensive_installer.py", "--all"],
                    "presentation": {
                        "reveal": "always",
                        "panel": "new"
                    }
                },
                {
                    "label": "GATE: Run Tests",
                    "type": "shell",
                    "command": f"{sys.executable}",
                    "args": ["-m", "pytest", "tests/", "-v"],
                    "presentation": {
                        "reveal": "always",
                        "panel": "shared"
                    }
                }
            ]
        }

        with open(vscode_dir / "tasks.json", "w") as f:
            json.dump(tasks, f, indent=4)

        # Recommended extensions
        extensions = {
            "recommendations": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "ms-python.black-formatter",
                "charliermarsh.ruff",
                "ms-toolsai.jupyter",
                "eamodio.gitlens",
                "github.copilot",
                "github.copilot-chat"
            ]
        }

        with open(vscode_dir / "extensions.json", "w") as f:
            json.dump(extensions, f, indent=4)

        print("✓ VS Code integration configured")
        print(f"  Location: {vscode_dir}")

    def setup_pycharm(self):
        """Setup PyCharm integration"""
        idea_dir = self.root / ".idea"
        idea_dir.mkdir(exist_ok=True)

        # Run configurations directory
        runConfigurations = idea_dir / "runConfigurations"
        runConfigurations.mkdir(exist_ok=True)

        # GATE Daemon configuration
        daemon_config = f"""<component name="ProjectRunConfigurationManager">
  <configuration default="false" name="GATE Daemon" type="PythonConfigurationType" factoryName="Python">
    <module name="{self.root.name}" />
    <option name="INTERPRETER_OPTIONS" value="" />
    <option name="PARENT_ENVS" value="true" />
    <envs>
      <env name="PYTHONUNBUFFERED" value="1" />
    </envs>
    <option name="SDK_HOME" value="{sys.executable}" />
    <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />
    <option name="IS_MODULE_SDK" value="false" />
    <option name="ADD_CONTENT_ROOTS" value="true" />
    <option name="ADD_SOURCE_ROOTS" value="true" />
    <option name="SCRIPT_NAME" value="$PROJECT_DIR$/gate_daemon.py" />
    <option name="PARAMETERS" value="" />
    <option name="SHOW_COMMAND_LINE" value="false" />
    <option name="EMULATE_TERMINAL" value="true" />
    <option name="MODULE_MODE" value="false" />
    <option name="REDIRECT_INPUT" value="false" />
    <option name="INPUT_FILE" value="" />
    <method v="2" />
  </configuration>
</component>"""

        with open(runConfigurations / "GATE_Daemon.xml", "w") as f:
            f.write(daemon_config)

        print("✓ PyCharm integration configured")
        print(f"  Location: {idea_dir}")

    def create_gate_snippets(self):
        """Create code snippets for GATE"""
        snippets_dir = self.root / ".vscode"
        snippets_dir.mkdir(exist_ok=True)

        snippets = {
            "GATE Problem Solver": {
                "prefix": "gate-solve",
                "body": [
                    "from gate_problem_solver import GateProblemSolver",
                    "",
                    "solver = GateProblemSolver()",
                    "# Analyze and fix code",
                    "analysis = solver.analyze_python_file(Path('${1:file.py}'))",
                    "print(analysis)"
                ],
                "description": "GATE problem solver template"
            },
            "GATE LLM Query": {
                "prefix": "gate-llm",
                "body": [
                    "from gate_llm_integration import llm_integration",
                    "",
                    "async def query_llm():",
                    "    response = await llm_integration.query_llm('${1:prompt}')",
                    "    print(response)"
                ],
                "description": "GATE LLM query template"
            },
            "GATE Memory Commit": {
                "prefix": "gate-memory",
                "body": [
                    "from gate_llm_integration import llm_integration",
                    "",
                    "llm_integration.commit_to_memory('${1:key}', ${2:value})"
                ],
                "description": "Commit to GATE memory"
            }
        }

        with open(snippets_dir / "gate.code-snippets", "w") as f:
            json.dump(snippets, f, indent=4)

        print("✓ GATE code snippets created")

    def setup_all(self):
        """Setup all IDE integrations"""
        print("\n" + "=" * 70)
        print("  GATE IDE INTEGRATION SETUP")
        print("=" * 70 + "\n")

        self.setup_vscode()
        print()
        self.setup_pycharm()
        print()
        self.create_gate_snippets()

        print("\n" + "=" * 70)
        print("  IDE INTEGRATION COMPLETE")
        print("=" * 70)
        print("\nConfigured:")
        print("  ✓ VS Code (settings, launch, tasks, extensions)")
        print("  ✓ PyCharm (run configurations)")
        print("  ✓ Code snippets")
        print("\nRestart your IDE to apply changes.")
        print("=" * 70 + "\n")


def main():
    """Main entry point"""
    integration = GateIDEIntegration()
    integration.setup_all()


if __name__ == "__main__":
    main()
