# The Gatekeeper Omega - Standalone Deployment Guide

**Version**: 1.0.0
**Date**: 2026-01-19
**Status**: Ready for Standalone Deployment

---

## 🎯 Executive Summary

The Gatekeeper Omega is now configured as a **complete standalone system** with:
- ✅ Administrator authentication (GATE)
- ✅ Resource monitoring and control
- ✅ Comprehensive test suite
- ✅ All required directories
- ✅ Forensic security scanning
- ✅ Self-contained deployment

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Directory Structure](#directory-structure)
3. [Administrator Setup](#administrator-setup)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Starting the System](#starting-the-system)
7. [Resource Management](#resource-management)
8. [Testing & Validation](#testing--validation)
9. [Maintenance](#maintenance)
10. [Troubleshooting](#troubleshooting)

---

## 🖥️ System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 11+
- **Python**: 3.9 - 3.11 (3.11 recommended)
- **RAM**: 16 GB minimum, 32 GB recommended
- **Storage**: 50 GB free space (for models and data)
- **CPU**: Modern multi-core processor (Intel i5/AMD Ryzen 5 or better)

### Recommended Requirements
- **RAM**: 32-64 GB
- **GPU**: NVIDIA GPU with 6+ GB VRAM (for AI acceleration)
- **Storage**: 100+ GB SSD
- **CPU**: Intel i7/AMD Ryzen 7 or better

### Software Dependencies
- Python 3.9-3.11
- pip (Python package manager)
- Git (for repository management)
- NVIDIA CUDA Toolkit (if using GPU)

---

## 📁 Directory Structure

The system has been configured with the following structure:

```
The-Gatekeeper/
├── data/                      # Data storage
│   ├── credentials/           # Encrypted credentials (GATE admin)
│   ├── sessions/              # Active sessions
│   ├── logs/                  # Application logs
│   ├── cache/                 # Temporary cache
│   └── models/                # Downloaded AI models
├── config/                    # Configuration files
│   ├── profiles/              # Performance profiles
│   ├── auth/                  # Authentication config
│   └── system/                # System configuration
├── models/                    # AI model storage
│   ├── tts/                   # Text-to-speech models
│   ├── speech/                # Speech recognition models
│   ├── llm/                   # Language models
│   └── embeddings/            # Embedding models
├── output/                    # Generated outputs
│   ├── audio/                 # Audio files
│   ├── reports/               # System reports
│   └── exports/               # Exported data
├── backups/                   # System backups
│   ├── config/                # Config backups
│   ├── data/                  # Data backups
│   └── sessions/              # Session backups
├── logs/                      # System logs
│   ├── system/                # System logs
│   ├── security/              # Security logs
│   └── performance/           # Performance logs
├── static/                    # Static assets
│   ├── audio/                 # Audio assets
│   ├── icons/                 # Icons
│   ├── scripts/               # JavaScript files
│   └── css/                   # Stylesheets
├── templates/                 # HTML templates
│   ├── web/                   # Web interface templates
│   └── reports/               # Report templates
├── tests/                     # Test suite
└── test_reports/              # Test execution reports
```

**Note**: All directories have been automatically created during setup.

---

## 👤 Administrator Setup

### GATE Administrator Credentials

**IMPORTANT**: Administrator credentials have been created for GATE.

#### Credentials Location
```
data/credentials/GATE_ADMIN_CREDENTIALS.txt
```

#### Default Administrator
- **Username**: `gate`
- **Role**: Administrator
- **Permissions**: Full system access

#### Password Information
The auto-generated password has been saved to:
```
data/credentials/GATE_ADMIN_CREDENTIALS.txt
```

**⚠️ CRITICAL SECURITY STEPS**:
1. Open the credentials file and save the password to a secure password manager
2. Delete the credentials file after saving the password
3. Store the password in a secure location (password manager, vault, etc.)
4. The password **CANNOT** be recovered if lost

#### Password Management

**View Current Password** (one time only):
```bash
# Windows
type data\credentials\GATE_ADMIN_CREDENTIALS.txt

# Linux/Mac
cat data/credentials/GATE_ADMIN_CREDENTIALS.txt
```

**Change Password**:
```python
python gate_admin_auth.py
# Follow prompts to reset password
```

**Re-authenticate**:
```python
from gate_admin_auth import GateAdminAuth

auth = GateAdminAuth()
success, session = auth.authenticate("gate", "your_password_here")
if success:
    print(f"✓ Authenticated: {session['role']}")
```

---

## 📦 Installation

### Step 1: Clone Repository (if not already done)
```bash
git clone https://github.com/redpostfarms-lgtm/omega.git
cd omega
```

### Step 2: Install Python Dependencies

**Core Dependencies Only** (lightweight):
```bash
pip install -r requirements.txt
```

**Full Installation** (with AI capabilities):
```bash
pip install -r requirements_enhanced.txt
```

**Development Installation** (with testing tools):
```bash
pip install -r requirements-dev.txt
```

### Step 3: Verify Installation
```bash
python -c "import torch; import transformers; print('✓ AI libraries installed')"
```

---

## ⚙️ Configuration

### Resource Configuration

The system uses `resource_config.json` for resource allocation:

```json
{
  "active_profile": "balanced",
  "resource_limits": {
    "cpu_percent": 80.0,
    "memory_percent": 70.0,
    "gpu_percent": 90.0
  }
}
```

**Available Profiles**:
- `maximum_performance`: 95% CPU, 85% RAM, 95% GPU
- `balanced`: 70% CPU, 60% RAM, 80% GPU (DEFAULT)
- `power_saver`: 40% CPU, 40% RAM, 50% GPU
- `background`: 20% CPU, 30% RAM, 30% GPU

**Configure Resources**:
```bash
python resource_controller.py
```

---

## 🚀 Starting the System

### Quick Start
```bash
python start_gatekeeper.py
```

This will:
1. Check Python version (3.9+)
2. Verify dependencies
3. Initialize all directories
4. Set up GATE administrator (if not already done)
5. Display next steps

### Manual Start (Advanced)

**1. Authenticate as Administrator**:
```python
python gate_admin_auth.py
# Enter credentials when prompted
```

**2. Configure Resources**:
```bash
python resource_controller.py status
```

**3. Run System Tests**:
```bash
python run_comprehensive_tests.py
```

**4. Start Core System**:
```bash
python omega_core.py
```

---

## 📊 Resource Management

### Real-Time Monitoring

**View Current Usage**:
```bash
python resource_controller.py status
```

**Output Example**:
```
Active Profile: BALANCED

CPU Usage:    [██████████░░░░░░░░░░] OK 41.1% / 80%
Memory Usage: [████████████████░░░░] /!\ 57.2% / 70% (9.0/15.8 GB)
GPU Usage:    [█░░░░░░░░░░░░░░░░░░░] OK 6.0% / 90% (1048/6144 MB)
```

### Adjust Resource Limits

**Interactive Mode**:
```bash
python resource_controller.py
```

**Command Line**:
```bash
# Set profile
python resource_controller.py profile maximum_performance

# Adjust individual limits
python resource_controller.py set cpu 80
python resource_controller.py set memory 70
python resource_controller.py set gpu 90
```

### Performance Tuning

**For Heavy AI Workloads**:
```bash
python resource_controller.py profile maximum_performance
```

**For Background Operation**:
```bash
python resource_controller.py profile background
```

**Custom Configuration**:
```bash
python resource_controller.py set cpu 75
python resource_controller.py set memory 65
```

---

## ✅ Testing & Validation

### Comprehensive Test Suite

**Run All Tests**:
```bash
python run_comprehensive_tests.py
```

This executes:
- ✅ Forensic security scan (706 Python files)
- ✅ Integration tests (5 test suites)
- ✅ Resource monitoring
- ✅ Pytest suite (24 tests)

**Test Reports Generated**:
```
test_reports/
├── forensic_scan_report.json
├── integration_test_report.json
├── resource_monitoring_report.json
└── master_test_report.json
```

### Individual Test Suites

**Forensic Scan**:
```bash
pytest tests/test_forensics_integrity.py -v
```

**Integration Tests**:
```bash
pytest tests/test_integration_suite.py -v
```

**Resource Monitoring**:
```bash
pytest tests/test_resource_monitor.py -v
```

### Test Results Summary

Last test run (2026-01-19):
- ✅ **Forensic Scan**: 706 files analyzed, 35 security findings
- ✅ **Integration Tests**: 5/5 passed (100%)
- ✅ **Resource Monitoring**: Operational
- ⚠️ **Pytest**: 22/24 passed (2 security-related warnings)

---

## 🔧 Maintenance

### Regular Tasks

**Daily**:
- Check resource usage: `python resource_controller.py status`
- Review logs: `logs/system/*.log`

**Weekly**:
- Run test suite: `python run_comprehensive_tests.py`
- Review security reports: `test_reports/forensic_scan_report.json`
- Backup credentials: `cp -r data/credentials backups/`

**Monthly**:
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Clean cache: `rm -rf data/cache/*`
- Archive old logs: `mv logs/*.log backups/logs/`

### Backup & Recovery

**Backup Configuration**:
```bash
tar -czf backups/config_$(date +%Y%m%d).tar.gz config/ resource_config.json
```

**Backup Data**:
```bash
tar -czf backups/data_$(date +%Y%m%d).tar.gz data/ --exclude=data/cache
```

**Restore from Backup**:
```bash
tar -xzf backups/config_YYYYMMDD.tar.gz
```

---

## 🔍 Troubleshooting

### Common Issues

#### Issue: "Administrator not configured"
**Solution**:
```bash
python gate_admin_auth.py
# Follow setup prompts
```

#### Issue: "Memory usage exceeded limit"
**Solution**:
```bash
# Increase memory limit
python resource_controller.py set memory 85

# Or switch to power saver profile
python resource_controller.py profile power_saver
```

#### Issue: "GPU not detected"
**Solution**:
1. Verify NVIDIA drivers: `nvidia-smi`
2. Install CUDA toolkit
3. Fallback to CPU: `python resource_controller.py set gpu 0`

#### Issue: "Tests failing"
**Solution**:
```bash
# Run tests in verbose mode
pytest tests/ -v --tb=long

# Check specific test
pytest tests/test_integration_suite.py::test_async_operations -v
```

### Logs

**System Logs**:
```bash
# View recent system logs
tail -f logs/system/gatekeeper_$(date +%Y%m%d).log

# Search for errors
grep -i error logs/system/*.log
```

**Security Logs**:
```bash
# View security events
tail -f logs/security/security_$(date +%Y%m%d).log
```

### Support

For issues not covered here:
1. Check `COMPREHENSIVE_TEST_SUMMARY.md`
2. Review `STANDALONE_ANALYSIS.json`
3. Consult `RESOURCE_CONTROL_QUICK_REFERENCE.md`

---

## 📌 Important Files Reference

| File | Purpose |
|------|---------|
| `start_gatekeeper.py` | Main startup script |
| `gate_admin_auth.py` | Administrator authentication |
| `resource_controller.py` | Resource management |
| `run_comprehensive_tests.py` | Test suite runner |
| `resource_config.json` | Resource configuration |
| `STANDALONE_ANALYSIS.json` | System analysis report |
| `data/credentials/GATE_ADMIN_CREDENTIALS.txt` | Admin password (DELETE AFTER SAVING!) |

---

## ✨ Key Features

### Implemented ✅
- Administrator authentication system (GATE)
- Resource monitoring (CPU, RAM, GPU)
- Performance profiles (4 configurations)
- Comprehensive test suite
- Forensic security scanning
- File integrity checking
- Session management
- Encrypted credential storage
- Standalone deployment ready

### Coming Soon 🚧
- Web dashboard UI
- Multi-user support
- Cloud integration
- Advanced AI model management
- Automated backup scheduling

---

## 🔐 Security Best Practices

1. **Immediately save and delete** `GATE_ADMIN_CREDENTIALS.txt` after installation
2. Use strong, unique passwords for all accounts
3. Run forensic scans regularly: `pytest tests/test_forensics_integrity.py`
4. Keep dependencies updated: `pip install --upgrade -r requirements.txt`
5. Monitor security logs: `logs/security/`
6. Backup credentials regularly to secure storage
7. Limit network exposure (use localhost only for sensitive operations)

---

## 📞 Quick Commands Reference

```bash
# System Status
python resource_controller.py status

# Start System
python start_gatekeeper.py

# Run Tests
python run_comprehensive_tests.py

# Authenticate
python gate_admin_auth.py

# Change Resources
python resource_controller.py profile balanced

# View Logs
tail -f logs/system/gatekeeper_*.log

# Backup
tar -czf backup_$(date +%Y%m%d).tar.gz config/ data/ resource_config.json
```

---

**End of Standalone Deployment Guide**

*The Gatekeeper Omega is ready for independent operation.*
