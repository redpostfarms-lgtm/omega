# Scripts Directory

This directory contains utility scripts, automation workflows, and monitoring tools for the Gatekeeper system.

## Directory Structure

```
scripts/
├── automation/   # Automated workflows and scheduled tasks
├── utilities/    # Helper scripts and tools
└── monitoring/   # System monitoring and health check scripts
```

## Script Categories

### Automation (`automation/`)
Scripts that run automatically or on schedule:
- Data collection pipelines
- Report generation
- System maintenance tasks
- Backup and archival workflows

### Utilities (`utilities/`)
Helper scripts for common tasks:
- Data validation
- File conversion
- Configuration management
- Testing utilities

### Monitoring (`monitoring/`)
System health and performance scripts:
- Metrics collection
- Alert generation
- Performance benchmarking
- Log analysis

## Usage

### Running Scripts

#### Python Scripts
```bash
python scripts/automation/collect_metrics.py
python scripts/utilities/validate_config.py --config config.json
```

#### With Arguments
```bash
python scripts/monitoring/health_check.py \
  --prometheus-url http://localhost:9090 \
  --alert-threshold 80
```

### Scheduling Scripts

#### Windows Task Scheduler
Create a scheduled task for regular execution:
```powershell
schtasks /create /tn "MetricsCollection" /tr "python C:\path\to\script.py" /sc daily /st 00:00
```

#### Cron (WSL/Linux)
```bash
# Edit crontab
crontab -e

# Run every hour
0 * * * * python /path/to/scripts/monitoring/collect.py

# Run daily at midnight
0 0 * * * python /path/to/scripts/automation/daily_report.py
```

## Script Template

### Python Script Template
```python
#!/usr/bin/env python3
"""
Script Name: my_script.py
Description: Brief description of what this script does
Author: Your Name
Date: 2026-01-18
"""

import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main(args):
    """Main script logic"""
    logger.info("Script started")

    # Your code here

    logger.info("Script completed successfully")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script description")
    parser.add_argument("--input", help="Input file path")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        main(args)
    except Exception as e:
        logger.error(f"Script failed: {e}", exc_info=True)
        exit(1)
```

## Best Practices

1. **Documentation**: Add docstrings and comments
2. **Error Handling**: Use try/except and log errors
3. **Arguments**: Use argparse for command-line options
4. **Logging**: Use logging module instead of print
5. **Validation**: Validate inputs before processing
6. **Idempotency**: Scripts should be safe to run multiple times
7. **Dependencies**: Document required packages at the top

## Common Scripts

### Example: Metrics Collection
```python
# scripts/monitoring/collect_metrics.py
import requests
import pandas as pd
from datetime import datetime

def collect_system_metrics():
    """Collect metrics from Prometheus"""
    metrics = {
        'timestamp': datetime.now(),
        'cpu_usage': get_cpu_metric(),
        'memory_usage': get_memory_metric(),
        'request_rate': get_request_rate()
    }

    df = pd.DataFrame([metrics])
    df.to_csv(f'data/raw/metrics_{datetime.now():%Y%m%d}.csv',
              mode='a', header=False, index=False)
```

### Example: Report Generator
```python
# scripts/automation/generate_report.py
from pathlib import Path
import matplotlib.pyplot as plt

def generate_daily_report():
    """Generate daily performance report"""
    data = load_metrics()

    fig = create_dashboard(data)
    fig.savefig(f'reports/visualizations/daily_{datetime.now():%Y%m%d}.png')

    send_email_notification()
```

## Integration

Scripts can be called from:
- Notebooks (via `%run` magic or subprocess)
- Other scripts (via imports)
- Command line (manual or scheduled)
- GitHub Actions / CI/CD pipelines

## Testing

Test scripts before automation:
```bash
# Dry run
python scripts/automation/backup.py --dry-run

# Verbose mode
python scripts/monitoring/health.py --verbose
```
