# Data Directory

This directory stores datasets and cached data for the Gatekeeper system.

## Directory Structure

```
data/
├── raw/         # Original, immutable data
├── processed/   # Cleaned and transformed data
└── cache/       # Temporary cached data and intermediate results
```

## Usage Guidelines

### Raw Data (`raw/`)
- **Never modify** files in this directory
- Store original datasets exactly as received
- Document data sources in filenames or metadata

### Processed Data (`processed/`)
- Cleaned and validated datasets
- Feature-engineered data
- Ready for analysis or model training

### Cache (`cache/`)
- Temporary computations
- Can be safely deleted
- Automatically regenerated as needed

## Data Formats

### Recommended Formats
- **CSV**: Tabular data, human-readable
- **Parquet**: Large datasets, efficient compression
- **JSON**: Structured configuration or API responses
- **HDF5**: Multi-dimensional arrays, time series
- **SQLite**: Relational data, queryable

### Example Usage
```python
import pandas as pd

# Load raw data
df = pd.read_csv('data/raw/metrics_2026-01.csv')

# Process and save
df_clean = process_data(df)
df_clean.to_parquet('data/processed/metrics_2026-01_clean.parquet')

# Cache intermediate results
cache_path = 'data/cache/temp_analysis.pkl'
df.to_pickle(cache_path)
```

## Data Management

### Versioning
Track data versions in filenames:
```
metrics_v1.0_2026-01-18.csv
model_training_data_v2.1.parquet
```

### Cleanup
Cache directory should be cleaned regularly:
```bash
# Clear cache older than 7 days
find data/cache -type f -mtime +7 -delete
```

### Git Configuration
Data files are gitignored to prevent bloating the repository.

For small, critical datasets, use Git LFS:
```bash
git lfs track "data/raw/*.csv"
git add .gitattributes
```

## Security

**Never commit**:
- Personally Identifiable Information (PII)
- API keys or credentials
- Production database dumps
- Large files (>100MB)

Use `.gitignore` to exclude sensitive data:
```
data/raw/sensitive_*
data/raw/*_credentials.json
```

## Best Practices

1. **Document Sources**: Include metadata about data origin
2. **Validate Early**: Check data integrity immediately after acquisition
3. **Compress Large Files**: Use parquet, gzip, or zip for storage
4. **Separate Concerns**: Keep raw data pristine, work with copies
5. **Regular Backups**: Critical datasets should be backed up externally
