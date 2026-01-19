# Resource Control Quick Reference Guide

## 🎯 Quick Commands

### View Current Resource Usage
```bash
python resource_controller.py status
```
**Output**: Real-time CPU, RAM, and GPU usage with visual progress bars

---

## 🔧 Adjust Resource Limits

### Performance Profiles

| Profile | CPU | RAM | GPU | Use Case |
|---------|-----|-----|-----|----------|
| **maximum_performance** | 95% | 85% | 95% | Heavy AI workloads |
| **balanced** | 70% | 60% | 80% | Normal operation (DEFAULT) |
| **power_saver** | 40% | 40% | 50% | Low power mode |
| **background** | 20% | 30% | 30% | Background tasks |

### Set a Profile
```bash
# Maximum AI performance
python resource_controller.py profile maximum_performance

# Balanced (default)
python resource_controller.py profile balanced

# Power saver
python resource_controller.py profile power_saver

# Background mode
python resource_controller.py profile background
```

---

## ⚙️ Manual Adjustments

### Adjust Individual Resources
```bash
# Set CPU limit
python resource_controller.py set cpu 80

# Set Memory limit
python resource_controller.py set memory 70

# Set GPU limit
python resource_controller.py set gpu 90
```

---

## 🖥️ Interactive Mode

```bash
python resource_controller.py
```

**Interactive Menu**:
1. Maximum Performance
2. Balanced
3. Power Saver
4. Background
5. Set CPU Limit (custom)
6. Set Memory Limit (custom)
7. Set GPU Limit (custom)
8. Refresh Status
9. Save & Exit
0. Exit Without Saving

---

## 📊 Test Suite

### Run All Tests
```bash
python run_comprehensive_tests.py
```

**Includes**:
- ✅ Forensic security scan
- ✅ Integration tests
- ✅ Resource monitoring
- ✅ Pytest suite

### Run Specific Tests
```bash
# Run only pytest suite
pytest tests/ -v

# Run integration tests
pytest tests/test_integration_suite.py -v

# Run resource monitoring tests
pytest tests/test_resource_monitor.py -v

# Run forensic scan
pytest tests/test_forensics_integrity.py -v
```

---

## 📈 Current Resource Usage (Example)

```
Active Profile: BALANCED

CPU Usage:    [██████████░░░░░░░░░░] OK 41.1% / 80%
Memory Usage: [████████████████░░░░] /!\ 57.2% / 70% (9.0/15.8 GB)
GPU Usage:    [█░░░░░░░░░░░░░░░░░░░] OK 6.0% / 90% (1048/6144 MB)
```

### Status Indicators
- `OK` - Within limits
- `/!\` - Approaching limit (>80% of limit)
- `<!>` - Exceeded limit

---

## 🔍 Monitoring Interpretation

### CPU Usage
- **<40%**: Light usage, good headroom
- **40-70%**: Moderate usage, normal operation
- **70-90%**: High usage, may need optimization
- **>90%**: Critical, consider limiting AI workloads

### Memory Usage
- **<50%**: Plenty of RAM available
- **50-70%**: Moderate usage, acceptable
- **70-85%**: High usage, monitor closely
- **>85%**: Critical, may cause system slowdown

### GPU Usage
- **<30%**: GPU underutilized
- **30-60%**: Good utilization
- **60-90%**: High utilization, optimal for AI
- **>90%**: Maximum load, ensure cooling is adequate

---

## 🎛️ Recommended Settings by Workload

### AI Model Training
```bash
python resource_controller.py profile maximum_performance
```
- CPU: 95%
- RAM: 85%
- GPU: 95%

### Real-time Voice Processing
```bash
python resource_controller.py set cpu 80
python resource_controller.py set memory 70
python resource_controller.py set gpu 80
```

### Background Monitoring
```bash
python resource_controller.py profile background
```
- CPU: 20%
- RAM: 30%
- GPU: 30%

### Development/Testing
```bash
python resource_controller.py profile balanced
```
- CPU: 70%
- RAM: 60%
- GPU: 80%

---

## 📁 Configuration File

**Location**: `resource_config.json`

**Manual Edit**:
```json
{
  "active_profile": "balanced",
  "resource_limits": {
    "cpu_percent": 70.0,
    "memory_percent": 60.0,
    "gpu_percent": 80.0
  }
}
```

---

## 🚨 Troubleshooting

### Issue: Memory usage exceeds limit during AI inference

**Solution**:
```bash
# Option 1: Increase memory limit
python resource_controller.py set memory 85

# Option 2: Switch to power saver profile
python resource_controller.py profile power_saver
```

### Issue: GPU not detected

**Check**:
1. Ensure NVIDIA drivers are installed
2. Run: `nvidia-smi` to verify GPU visibility
3. Install CUDA toolkit if needed

**Fallback**:
```bash
# Force CPU-only mode by setting GPU limit to 0
python resource_controller.py set gpu 0
```

### Issue: System becomes slow during AI processing

**Solution**:
```bash
# Reduce CPU and memory limits
python resource_controller.py set cpu 60
python resource_controller.py set memory 50
```

---

## 📊 Resource Reports

### View Last Test Report
```bash
# On Linux/Mac
cat test_reports/master_test_report.json | jq

# On Windows
type test_reports\master_test_report.json
```

### Report Locations
- `test_reports/forensic_scan_report.json` - Security scan results
- `test_reports/integration_test_report.json` - Integration test results
- `test_reports/resource_monitoring_report.json` - Resource usage data
- `test_reports/master_test_report.json` - Consolidated report

---

## 🔄 Common Workflows

### Daily AI Development
```bash
# Morning: Set balanced profile
python resource_controller.py profile balanced

# Check status periodically
python resource_controller.py status

# Evening: Switch to background for overnight processing
python resource_controller.py profile background
```

### Before Heavy AI Training
```bash
# 1. Check current usage
python resource_controller.py status

# 2. Set maximum performance
python resource_controller.py profile maximum_performance

# 3. Monitor during training
watch -n 5 python resource_controller.py status
```

### System Maintenance
```bash
# 1. Reduce to minimal usage
python resource_controller.py profile background

# 2. Run tests
python run_comprehensive_tests.py

# 3. Restore normal operation
python resource_controller.py profile balanced
```

---

## 💡 Pro Tips

1. **Monitor First**: Always check `status` before making changes
2. **Gradual Adjustments**: Change limits in small increments (5-10%)
3. **Save Configuration**: Use menu option 9 or let CLI save automatically
4. **Test Changes**: Monitor for a few minutes after adjustment
5. **Document Settings**: Note which profile works best for your workload

---

## 📞 Need Help?

- Review comprehensive summary: `COMPREHENSIVE_TEST_SUMMARY.md`
- Run full test suite: `python run_comprehensive_tests.py`
- Check resource config: `resource_config.json`

---

**Last Updated**: 2026-01-19
