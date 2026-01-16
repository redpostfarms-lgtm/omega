# Auto Tool Manager - Complete Guide

## Overview

The Auto Tool Manager is an intelligent tool management system that automatically detects, accesses, and installs required tools when needed. It eliminates manual dependency management and ensures your projects have the right tools available at the right time.

## Components

### 1. **auto_tool_manager.py** - Core Detection & Installation
Main tool management engine that:
- Detects installed tools (Java, Gradle, Maven, Python, Git, Node.js, Docker, etc.)
- Automatically installs missing tools on Windows, macOS, and Linux
- Maintains a registry of available tools
- Generates status reports

**Key Classes:**
- `ToolDetector` - Detects available tools and versions
- `ToolInstaller` - Installs tools using system package managers
- `AutoToolManager` - Orchestrates detection and installation

### 2. **tool_access_manager.py** - On-Demand Access Layer
Smart tool access system that:
- Caches tool information for faster access
- Provides on-demand tool access with auto-ensure
- Routes build commands to appropriate tools
- Manages tool execution with fallbacks

**Key Classes:**
- `ToolAccessManager` - Manages on-demand tool access
- `SmartToolRouter` - Intelligently routes commands to appropriate tools

### 3. **auto_tool_launcher.py** - User-Friendly Interface
Simple command-line interface for common operations

## Installation & Setup

### Prerequisites
- Python 3.8+
- Administrator/sudo access (for tool installation on some systems)

### First Run
```bash
# Detect all available tools
python auto_tool_launcher.py detect

# Show status
python auto_tool_launcher.py status
```

## Usage Examples

### Detect Available Tools
```bash
python auto_tool_launcher.py detect
```
Output:
```
=== Auto Tool Detection Started ===
✓ java found: openjdk version "21.0.1" 2023-10-17
✓ gradle found: gradle/wrapper/gradle-wrapper.jar
✗ maven not found
✓ python found: Python 3.11.0
✓ git found: git version 2.40.0
```

### Ensure a Specific Tool
```bash
# Ensure Java is available
python auto_tool_launcher.py ensure --tool java

# Ensure Gradle is available
python auto_tool_launcher.py ensure --tool gradle

# Ensure Maven is available
python auto_tool_launcher.py ensure --tool maven
```

### Ensure All Tools for a Project
```bash
# Check and install tools for a Maven project
python auto_tool_launcher.py project --project ./my-maven-project

# Check and install tools for a Gradle project
python auto_tool_launcher.py project --project ./my-gradle-project
```

### Auto-Build a Project
```bash
# Automatically detect build tool and build
python auto_tool_launcher.py build --project ./my-project
```

### Show Tool Status
```bash
python auto_tool_launcher.py status
```

## Python Integration

### For Developers

#### 1. Detect & Ensure Java
```python
from tool_access_manager import ensure_java

# Ensure Java 21 is available
if ensure_java('21'):
    print("Java is ready!")
```

#### 2. Access Tools for Projects
```python
from tool_access_manager import ToolAccessManager

manager = ToolAccessManager()
tools = manager.access_tools_for_project('./my-project')
print(f"Available tools: {tools}")
```

#### 3. Run Tools
```python
from tool_access_manager import get_tool_manager

manager = get_tool_manager()
result = manager.run_tool('gradle', ['build', '--info'])
```

#### 4. Smart Build
```python
from tool_access_manager import run_build

# Automatically detect build tool and execute build
run_build('./my-project', '--info')
```

#### 5. Complete Tool Management
```python
from auto_tool_manager import AutoToolManager

manager = AutoToolManager()
manager.setup()

# Ensure tools for project
status = manager.ensure_project_tools('./my-gradle-project', auto_install=True)
print(f"Status: {status}")

# Generate report
manager.report()
manager.save_report('tools_report.json')
```

## Configuration

### Tool Cache
Tools are cached in `tool_cache.json` for faster access:
```json
{
  "tools": {
    "java": "/usr/bin/java",
    "gradle": "/usr/bin/gradle",
    "python": "/usr/bin/python3"
  },
  "paths": {
    "java": "/usr/bin/java",
    "gradle": "/usr/bin/gradle"
  }
}
```

### Logging
Logs are saved to `auto_tool_manager.log` for debugging and auditing.

## Project Auto-Detection

The system automatically detects project types:
- **Maven** - Looks for `pom.xml` → requires Java + Maven
- **Gradle** - Looks for `build.gradle`, `build.gradle.kts`, `gradlew` → requires Java + Gradle
- **Node.js** - Looks for `package.json` → requires Node.js + npm

## Platform Support

### Windows
- Uses Chocolatey (if installed) or winget for package management
- Supports all major tools

### macOS
- Uses Homebrew for package management
- Fast installation and setup

### Linux
- Uses apt (Ubuntu/Debian) or yum (RHEL/CentOS)
- Automatic package manager detection

## Supported Tools

| Tool | Windows | macOS | Linux | Auto-Install |
|------|---------|-------|-------|--------------|
| Java | ✓ | ✓ | ✓ | ✓ |
| Gradle | ✓ | ✓ | ✓ | ✓ |
| Maven | ✓ | ✓ | ✓ | ✓ |
| Python | ✓ | ✓ | ✓ | Manual |
| Git | ✓ | ✓ | ✓ | Manual |
| Node.js | ✓ | ✓ | ✓ | ✓ |
| Docker | ✓ | ✓ | ✓ | Manual |

## Advanced Usage

### Custom Tool Registration
```python
from auto_tool_manager import AutoToolManager

manager = AutoToolManager()
manager.setup()

# Register custom tool
def detect_custom():
    return subprocess.run(['custom-tool', '--version']).returncode == 0

def install_custom():
    # Custom installation logic
    return True

manager.register_tool('custom-tool', detect_custom, install_custom, required=True)

# Use it
manager.auto_ensure_tool('custom-tool')
```

### Batch Tool Verification
```python
from auto_tool_manager import AutoToolManager

manager = AutoToolManager()
manager.setup()

# Detect all tools
manager.detector.detect_all_tools()

# Get report
report = manager.report()

# Save for CI/CD
manager.save_report('ci_tool_requirements.json')
```

## Troubleshooting

### Java Not Installing
1. Ensure you have Chocolatey (Windows) or Homebrew (macOS) installed
2. Run with admin/sudo privileges
3. Check logs: `tail -f auto_tool_manager.log`
4. Manual install: Download from https://adoptium.net/

### Build Tool Not Found
```bash
# Clear cache and re-detect
rm tool_cache.json
python auto_tool_launcher.py detect
```

### Permission Denied (Linux/macOS)
```bash
# Grant execute permissions
chmod +x auto_tool_manager.py auto_tool_launcher.py tool_access_manager.py
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Setup Build Tools
  run: |
    python auto_tool_launcher.py detect
    python auto_tool_launcher.py ensure --tool java
    python auto_tool_launcher.py project --project .
```

### Jenkins
```groovy
stage('Setup Tools') {
    steps {
        sh 'python auto_tool_launcher.py detect'
        sh 'python auto_tool_launcher.py project --project .'
    }
}
```

## Performance Tips

1. **First run** - Caches all tool information for fast subsequent access
2. **Tool registration** - Register only tools your project needs
3. **Lazy loading** - Tools are accessed on-demand, not all at startup
4. **Cache clearing** - Delete `tool_cache.json` to force re-detection

## Security

- Tools are verified before execution
- Install sources are from official package managers
- Logging captures all tool operations for auditing
- No credentials stored in cache files

## Future Enhancements

- [ ] Docker image support
- [ ] Container environment detection
- [ ] Tool version pinning
- [ ] Dependency resolution graph
- [ ] Performance benchmarking
- [ ] Integration with IDEs

## Support

For issues or questions:
1. Check logs: `auto_tool_manager.log`
2. Run detection: `python auto_tool_launcher.py detect`
3. Check cache: `tool_cache.json`

## License

Auto Tool Manager - Part of The Gatekeeper system
