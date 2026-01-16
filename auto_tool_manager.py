#!/usr/bin/env python3
"""
Auto Tool Manager - Automatically detects and accesses required tools on-demand
Handles installation, configuration, and version management of system tools
"""

import os
import sys
import json
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import tempfile

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_tool_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ToolDetector:
    """Detects available tools and their versions"""
    
    def __init__(self):
        self.system = platform.system()
        self.tools_found = {}
        self.tools_missing = {}
    
    def detect_tool(self, tool_name: str, version_flag: str = '--version') -> Optional[str]:
        """Detect if a tool is available and get its version"""
        try:
            result = subprocess.run(
                [tool_name, version_flag],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                self.tools_found[tool_name] = version
                logger.info(f"✓ {tool_name} found: {version}")
                return version
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        self.tools_missing[tool_name] = True
        logger.warning(f"✗ {tool_name} not found")
        return None
    
    def detect_java(self) -> Optional[Tuple[str, str]]:
        """Detect Java installation and version"""
        try:
            result = subprocess.run(
                ['java', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            version_str = (result.stderr + result.stdout).strip().split('\n')[0]
            if result.returncode == 0:
                self.tools_found['java'] = version_str
                logger.info(f"✓ Java found: {version_str}")
                return ('java', version_str)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        self.tools_missing['java'] = True
        logger.warning("✗ Java not found")
        return None
    
    def detect_gradle(self) -> Optional[str]:
        """Detect Gradle installation"""
        gradle_paths = [
            'gradle',
            './gradlew',
            './gradle/wrapper/gradle-wrapper.jar'
        ]
        for gradle in gradle_paths:
            if shutil.which(gradle) or os.path.exists(gradle):
                self.tools_found['gradle'] = gradle
                logger.info(f"✓ Gradle found at: {gradle}")
                return gradle
        
        self.tools_missing['gradle'] = True
        logger.warning("✗ Gradle not found")
        return None
    
    def detect_maven(self) -> Optional[str]:
        """Detect Maven installation"""
        try:
            result = subprocess.run(
                ['mvn', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.tools_found['maven'] = result.stdout.strip().split('\n')[0]
                logger.info(f"✓ Maven found: {self.tools_found['maven']}")
                return 'maven'
        except FileNotFoundError:
            pass
        
        self.tools_missing['maven'] = True
        logger.warning("✗ Maven not found")
        return None
    
    def detect_python(self) -> Optional[str]:
        """Detect Python installation"""
        return self.detect_tool('python', '--version')
    
    def detect_all_tools(self) -> Dict:
        """Detect all commonly used tools"""
        logger.info("=== Auto Tool Detection Started ===")
        
        tools_to_detect = {
            'java': self.detect_java,
            'gradle': self.detect_gradle,
            'maven': self.detect_maven,
            'python': self.detect_python,
            'git': lambda: self.detect_tool('git', '--version'),
            'node': lambda: self.detect_tool('node', '--version'),
            'npm': lambda: self.detect_tool('npm', '--version'),
            'docker': lambda: self.detect_tool('docker', '--version'),
        }
        
        results = {}
        for tool, detector in tools_to_detect.items():
            try:
                results[tool] = detector()
            except Exception as e:
                logger.error(f"Error detecting {tool}: {e}")
                results[tool] = None
        
        logger.info(f"=== Detection Complete ===")
        logger.info(f"Found: {list(self.tools_found.keys())}")
        logger.info(f"Missing: {list(self.tools_missing.keys())}")
        
        return results


class ToolInstaller:
    """Handles tool installation and setup"""
    
    def __init__(self):
        self.system = platform.system()
        self.install_log = []
    
    def install_java_21(self) -> bool:
        """Auto-install Java 21 LTS"""
        logger.info("Installing Java 21 LTS...")
        
        try:
            if self.system == 'Windows':
                return self._install_java_windows()
            elif self.system == 'Darwin':
                return self._install_java_macos()
            elif self.system == 'Linux':
                return self._install_java_linux()
        except Exception as e:
            logger.error(f"Failed to install Java: {e}")
            return False
    
    def _install_java_windows(self) -> bool:
        """Install Java 21 on Windows"""
        try:
            # Try using Chocolatey
            if shutil.which('choco'):
                result = subprocess.run(
                    ['choco', 'install', 'openjdk21', '-y'],
                    capture_output=True,
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("✓ Java 21 installed via Chocolatey")
                    return True
            
            # Try using winget
            if shutil.which('winget'):
                result = subprocess.run(
                    ['winget', 'install', 'EclipseAdoptium.Temurin.21.JDK'],
                    capture_output=True,
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("✓ Java 21 installed via winget")
                    return True
        except Exception as e:
            logger.error(f"Windows installation failed: {e}")
        
        return False
    
    def _install_java_macos(self) -> bool:
        """Install Java 21 on macOS"""
        try:
            if shutil.which('brew'):
                result = subprocess.run(
                    ['brew', 'install', 'openjdk@21'],
                    capture_output=True,
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("✓ Java 21 installed via Homebrew")
                    return True
        except Exception as e:
            logger.error(f"macOS installation failed: {e}")
        
        return False
    
    def _install_java_linux(self) -> bool:
        """Install Java 21 on Linux"""
        try:
            # Try apt (Ubuntu/Debian)
            if shutil.which('apt'):
                subprocess.run(['sudo', 'apt', 'update'], capture_output=True, timeout=60)
                result = subprocess.run(
                    ['sudo', 'apt', 'install', '-y', 'openjdk-21-jdk'],
                    capture_output=True,
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("✓ Java 21 installed via apt")
                    return True
            
            # Try yum (RHEL/CentOS)
            elif shutil.which('yum'):
                result = subprocess.run(
                    ['sudo', 'yum', 'install', '-y', 'java-21-openjdk-devel'],
                    capture_output=True,
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("✓ Java 21 installed via yum")
                    return True
        except Exception as e:
            logger.error(f"Linux installation failed: {e}")
        
        return False
    
    def install_gradle(self) -> bool:
        """Auto-install Gradle"""
        logger.info("Installing Gradle...")
        try:
            if self.system == 'Windows' and shutil.which('choco'):
                result = subprocess.run(
                    ['choco', 'install', 'gradle', '-y'],
                    capture_output=True,
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("✓ Gradle installed via Chocolatey")
                    return True
            
            elif self.system in ['Darwin', 'Linux'] and shutil.which('brew'):
                result = subprocess.run(
                    ['brew', 'install', 'gradle'],
                    capture_output=True,
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("✓ Gradle installed via Homebrew")
                    return True
        except Exception as e:
            logger.error(f"Failed to install Gradle: {e}")
        
        return False
    
    def install_maven(self) -> bool:
        """Auto-install Maven"""
        logger.info("Installing Maven...")
        try:
            if self.system == 'Windows' and shutil.which('choco'):
                result = subprocess.run(
                    ['choco', 'install', 'maven', '-y'],
                    capture_output=True,
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("✓ Maven installed via Chocolatey")
                    return True
            
            elif self.system in ['Darwin', 'Linux'] and shutil.which('brew'):
                result = subprocess.run(
                    ['brew', 'install', 'maven'],
                    capture_output=True,
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("✓ Maven installed via Homebrew")
                    return True
        except Exception as e:
            logger.error(f"Failed to install Maven: {e}")
        
        return False


class AutoToolManager:
    """Main tool manager that orchestrates detection and installation"""
    
    def __init__(self):
        self.detector = ToolDetector()
        self.installer = ToolInstaller()
        self.tool_registry = {}
        self.required_tools = {}
    
    def register_tool(self, name: str, detector_func, installer_func, required: bool = False):
        """Register a tool with its detector and installer"""
        self.tool_registry[name] = {
            'detector': detector_func,
            'installer': installer_func,
            'required': required
        }
        if required:
            self.required_tools[name] = True
    
    def auto_ensure_tool(self, tool_name: str, auto_install: bool = True) -> bool:
        """
        Automatically ensure a tool is available.
        Detects it, and installs if missing and auto_install is True
        """
        logger.info(f"\n>>> Ensuring tool availability: {tool_name}")
        
        if tool_name not in self.tool_registry:
            logger.warning(f"Tool '{tool_name}' not registered")
            return False
        
        tool_info = self.tool_registry[tool_name]
        
        # Try to detect tool
        detected = tool_info['detector']()
        if detected:
            logger.info(f"✓ {tool_name} is already available")
            return True
        
        # Tool not found, try to install if auto_install is True
        if auto_install:
            logger.info(f"Installing {tool_name}...")
            if tool_info['installer']():
                logger.info(f"✓ {tool_name} installed successfully")
                return True
            else:
                logger.error(f"✗ Failed to install {tool_name}")
                return False
        
        return False
    
    def ensure_project_tools(self, project_path: str, auto_install: bool = True) -> Dict:
        """Ensure all required tools for a project are available"""
        logger.info(f"\n=== Ensuring Tools for Project: {project_path} ===")
        
        status = {
            'project': project_path,
            'available': [],
            'installed': [],
            'failed': []
        }
        
        # Detect project type and required tools
        project_path_obj = Path(project_path)
        
        build_files = {
            'pom.xml': 'maven',
            'build.gradle': 'gradle',
            'build.gradle.kts': 'gradle',
            'gradlew': 'gradle'
        }
        
        required_tools = set()
        
        for filename, tool in build_files.items():
            if (project_path_obj / filename).exists():
                required_tools.add(tool)
        
        # Always require Java for Maven/Gradle projects
        if required_tools:
            required_tools.add('java')
        
        logger.info(f"Detected required tools: {required_tools}")
        
        # Ensure each required tool
        for tool in required_tools:
            if tool not in self.tool_registry:
                continue
            
            if self.auto_ensure_tool(tool, auto_install):
                if tool in self.detector.tools_found:
                    status['available'].append(tool)
                else:
                    status['installed'].append(tool)
            else:
                status['failed'].append(tool)
        
        return status
    
    def setup(self):
        """Setup and register all tools"""
        logger.info("Setting up Auto Tool Manager...")
        
        # Register standard tools
        self.register_tool(
            'java',
            self.detector.detect_java,
            self.installer.install_java_21,
            required=True
        )
        
        self.register_tool(
            'gradle',
            self.detector.detect_gradle,
            self.installer.install_gradle
        )
        
        self.register_tool(
            'maven',
            self.detector.detect_maven,
            self.installer.install_maven
        )
        
        self.register_tool(
            'python',
            self.detector.detect_python,
            lambda: False  # Python already in use
        )
        
        self.register_tool(
            'git',
            lambda: self.detector.detect_tool('git', '--version'),
            lambda: False  # Manual setup recommended
        )
        
        logger.info("Auto Tool Manager ready!")
    
    def report(self):
        """Generate a tool status report"""
        report = {
            'system': self.detector.system,
            'tools_found': self.detector.tools_found,
            'tools_missing': list(self.detector.tools_missing.keys()),
            'registered_tools': list(self.tool_registry.keys())
        }
        
        logger.info("\n=== Tool Status Report ===")
        logger.info(json.dumps(report, indent=2))
        
        return report
    
    def save_report(self, filename: str = 'tool_status_report.json'):
        """Save tool status report to file"""
        report = self.report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to {filename}")
        return filename


def main():
    """Main entry point"""
    manager = AutoToolManager()
    manager.setup()
    
    # Get initial status
    manager.detector.detect_all_tools()
    manager.report()
    
    # Example: Ensure tools for current project
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        status = manager.ensure_project_tools(project_path, auto_install=True)
        logger.info(f"\nProject Tool Status: {status}")
    
    manager.save_report()


if __name__ == '__main__':
    main()
