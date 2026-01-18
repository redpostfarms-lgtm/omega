#!/usr/bin/env python3
"""
OMEGA Complete Setup & Dependency Manager
Installs all required and optional dependencies for full system functionality
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n{'='*60}")
    print(f"⚙️  {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"⚠️  Warning: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_python_version():
    """Verify Python version"""
    print("\n🐍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    if version.major == 3 and version.minor >= 8:
        print("   ✅ Compatible")
        return True
    else:
        print("   ❌ Requires Python 3.8+")
        return False

def install_dependencies():
    """Install all Python dependencies"""
    print("\n" + "="*60)
    print("📦 INSTALLING CORE DEPENDENCIES")
    print("="*60)
    
    core_deps = [
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "flask-socketio>=5.3.0",
        "qrcode[pil]>=7.4.0",
        "psutil>=5.9.0",
        "pillow>=10.0.0",
        "requests>=2.31.0"
    ]
    
    for dep in core_deps:
        run_command(f".venv\\Scripts\\pip install {dep}", f"Installing {dep}")
    
    print("\n" + "="*60)
    print("📦 INSTALLING OPTIONAL DEPENDENCIES")
    print("="*60)
    
    optional_deps = [
        ("python-dotenv", "Environment variable management"),
        ("colorama", "Colored terminal output"),
        ("rich", "Enhanced terminal UI"),
        ("pyngrok", "Python ngrok wrapper"),
    ]
    
    for dep, desc in optional_deps:
        run_command(f".venv\\Scripts\\pip install {dep}", f"Installing {dep} ({desc})")

def verify_installation():
    """Verify all critical imports work"""
    print("\n" + "="*60)
    print("🔍 VERIFYING INSTALLATION")
    print("="*60)
    
    imports = [
        ("flask", "Flask web framework"),
        ("flask_cors", "CORS support"),
        ("qrcode", "QR code generation"),
        ("psutil", "System monitoring"),
        ("PIL", "Image processing"),
        ("requests", "HTTP requests")
    ]
    
    all_ok = True
    for module, desc in imports:
        try:
            __import__(module)
            print(f"✅ {desc:30} OK")
        except ImportError:
            print(f"❌ {desc:30} FAILED")
            all_ok = False
    
    return all_ok

def create_venv_if_needed():
    """Create virtual environment if it doesn't exist"""
    if not os.path.exists(".venv"):
        print("\n🔧 Creating virtual environment...")
        run_command("python -m venv .venv", "Creating .venv")
        return True
    else:
        print("\n✅ Virtual environment exists")
        return False

def upgrade_pip():
    """Upgrade pip to latest version"""
    run_command(".venv\\Scripts\\python.exe -m pip install --upgrade pip", 
                "Upgrading pip to latest version")

def create_requirements_file():
    """Generate requirements.txt from installed packages"""
    print("\n📝 Generating requirements.txt...")
    run_command(".venv\\Scripts\\pip freeze > requirements.txt", 
                "Creating requirements.txt")

def main():
    print("="*60)
    print("⚡ OMEGA COMPLETE SETUP")
    print("   Full Dependency Installation & Verification")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup aborted: Incompatible Python version")
        return
    
    # Create venv if needed
    create_venv_if_needed()
    
    # Upgrade pip
    upgrade_pip()
    
    # Install all dependencies
    install_dependencies()
    
    # Verify installation
    if verify_installation():
        print("\n" + "="*60)
        print("✅ ALL DEPENDENCIES INSTALLED SUCCESSFULLY")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("⚠️  SOME DEPENDENCIES FAILED - CHECK ERRORS ABOVE")
        print("="*60)
    
    # Create requirements file
    create_requirements_file()
    
    print("\n" + "="*60)
    print("🚀 SETUP COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Start OMEGA Swarm: python omega_swarm_server.py")
    print("2. Or use launcher: LAUNCH_OMEGA.bat")
    print("3. Open control panel: http://10.0.0.26:5002")
    print("\n💡 For external access, configure tunnel:")
    print("   python setup_tunnel.py setup")
    print("="*60)

if __name__ == '__main__':
    main()
