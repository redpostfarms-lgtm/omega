# Reports Directory

This directory stores generated reports, visualizations, and output files from notebooks and monitoring systems.

## Directory Structure

```
reports/
├── visualizations/  # Exported charts, graphs, and visual reports
├── metrics/         # System metrics and performance reports
└── logs/            # Analysis logs and execution summaries
```

## Usage

### From Jupyter Notebooks
The `ReportGenerator` class in notebooks automatically saves outputs here:

```python
from pathlib import Path
report_gen = ReportGenerator(output_dir='./reports')

# Save figures
report_gen.save_figure(fig, 'dashboard')
report_gen.save_plotly(fig, 'network_graph')

# Export data
report_gen.export_data(df, 'metrics_data', formats=['csv', 'json'])
```

### From Python Scripts
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
# ... create visualization ...
fig.savefig('reports/visualizations/my_chart.png', dpi=300)
```

## Output Formats

### Visualizations
- PNG (high resolution, 300 DPI)
- PDF (vector format for reports)
- HTML (interactive Plotly charts)
- SVG (scalable vector graphics)

### Data
- CSV (tabular data)
- JSON (structured data)
- Excel (formatted reports)
- Parquet (efficient storage)

## File Naming Convention

Files are automatically timestamped:
```
dashboard_20260118_143045.png
metrics_data_20260118_143045.csv
```

## Cleanup

Reports accumulate over time. Clean up old files periodically:
```bash
# Remove files older than 30 days
find reports/ -type f -mtime +30 -delete
```

## Git Configuration

This directory is gitignored by default to prevent large binary files from being committed. To track specific reports, use:
```bash
git add -f reports/visualizations/important_report.png
```
