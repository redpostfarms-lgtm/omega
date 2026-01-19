# Notebooks Directory

This directory contains Jupyter notebooks for analysis, experimentation, and production workflows.

## Directory Structure

```
notebooks/
├── analysis/        # Exploratory data analysis and investigations
├── experiments/     # Experimental features and prototypes
└── production/      # Production-ready analysis notebooks
```

## Available Notebooks

### System Visualizations
- **system_visualizations.ipynb** - Comprehensive visualization dashboard
  - Interactive metrics monitoring
  - Network graph visualizations
  - Data analytics and statistical plots
  - Real-time Prometheus integration

## Usage

### Start Jupyter Lab
```bash
jupyter lab
```

### Start Jupyter Notebook
```bash
jupyter notebook
```

### Run Specific Notebook
```bash
jupyter notebook system_visualizations.ipynb
```

## Best Practices

1. **Naming Convention**: Use descriptive names with underscores
   - `system_metrics_analysis.ipynb`
   - `performance_benchmarking.ipynb`

2. **Organization**:
   - `/analysis` - One-off analyses and investigations
   - `/experiments` - Testing new features or approaches
   - `/production` - Finalized, reusable notebooks

3. **Documentation**: Add markdown cells to explain your analysis

4. **Version Control**: Clear outputs before committing
   ```bash
   jupyter nbconvert --clear-output --inplace *.ipynb
   ```

## Dependencies

All required packages are in `requirements.txt`. Additional notebook dependencies:
- jupyter / jupyterlab
- ipywidgets
- networkx
- kaleido (for Plotly exports)
- graphviz
- altair
- dash

Install with:
```bash
pip install -r requirements.txt
```
