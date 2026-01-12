# Database Guides Integration - Omega Control Panel

**Date:** January 2026  
**Developer:** Nick (Seattle)  
**Status:** Complete & Production-Ready

---

## Overview

This document explains how the two comprehensive database guides work together to provide a complete database management solution for the Omega Control Panel project.

---

## The Two Guides

### 1. [Flask-Migrate Setup Guide](./FLASK_MIGRATE_SETUP.md)

**Purpose:** Database schema management and migrations

**Covers:**
- Flask-Migrate installation and setup
- SQLAlchemy model creation
- Database migrations (create, apply, rollback)
- Batch mode for SQLite
- Troubleshooting common migration errors
- Best practices for naming constraints
- Real-world migration examples

**When to Use:**
- Setting up database migrations
- Creating or modifying database tables
- Managing schema changes over time
- Adding/removing columns, constraints, indexes
- Converting models from simple classes to SQLAlchemy

---

### 2. [PostgreSQL JSONB Query Guide](./POSTGRESQL_JSONB_QUERY_GUIDE.md)

**Purpose:** Advanced JSONB querying and optimization

**Covers:**
- JSONPath operators and syntax
- Variables and parameterization
- LATERAL joins for arrays
- Time-based filtering
- Top-N queries
- Grouping and analytics
- Indexing strategies (GIN, B-tree, expression indexes)
- Performance optimization
- Omega Control Panel use cases

**When to Use:**
- Querying JSONB columns efficiently
- Filtering and aggregating nested JSON data
- Optimizing query performance
- Building dashboards and analytics
- Working with device settings, alerts, and configurations

---

## How They Work Together

### Workflow: Schema Management → Querying

1. **Schema Setup (Flask-Migrate Guide)**
   ```python
   # Create models with JSONB columns
   class DeviceSettings(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       device_id = db.Column(db.String(80), unique=True)
       data = db.Column(db.JSON, nullable=False, default={})  # JSONB in PostgreSQL
   ```

2. **Create Migration**
   ```bash
   flask db migrate -m "add device_settings table"
   flask db upgrade
   ```

3. **Add Indexes (Flask-Migrate Guide)**
   ```python
   # In migration file
   op.create_index(
       'idx_data_gin',
       'device_settings',
       ['data'],
       postgresql_using='gin',
       postgresql_ops={'data': 'jsonb_path_ops'}
   )
   ```

4. **Query Efficiently (JSONB Query Guide)**
   ```sql
   -- Use optimized JSONB queries
   SELECT device_id, jsonb_path_query(data, '$.alerts[*] ? (@.severity >= 7)')
   FROM device_settings
   WHERE data @@ '$.status == "active"';
   ```

---

## Integration Examples

### Example 1: Adding JSONB Index via Migration

**Step 1:** Create migration (Flask-Migrate Guide)
```python
# migrations/versions/xxxx_add_jsonb_indexes.py
def upgrade():
    # GIN index for JSONB queries (from JSONB Query Guide)
    op.create_index(
        'idx_device_settings_data_gin',
        'device_settings',
        ['data'],
        postgresql_using='gin',
        postgresql_ops={'data': 'jsonb_path_ops'}
    )
    
    # Expression index for frequent path (from JSONB Query Guide)
    op.create_index(
        'idx_device_settings_fan_profile',
        'device_settings',
        [sa.text("(data->'config'->>'fan_profile')")],
        postgresql_where=sa.text("data->>'status' = 'active'")
    )
```

**Step 2:** Apply migration
```bash
flask db upgrade
```

**Step 3:** Use in queries (JSONB Query Guide)
```sql
-- Fast containment queries (uses GIN index)
SELECT * FROM device_settings
WHERE data @> '{"config": {"fan_profile": "quiet"}}';

-- Fast exact match (uses expression index)
SELECT * FROM device_settings
WHERE data -> 'config' ->> 'fan_profile' = 'quiet';
```

---

### Example 2: Hybrid Schema (Normal Columns + JSONB)

**Step 1:** Define model with hybrid approach (Flask-Migrate Guide)
```python
class DeviceSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(80), unique=True, nullable=False)
    
    # Normal columns for hot paths (fast B-tree indexes)
    status = db.Column(db.String(20))  # 'active', 'inactive'
    cpu_temp = db.Column(db.Numeric)   # for range queries
    
    # JSONB for flexible/variable data
    settings = db.Column(db.JSON, nullable=False, default={})
    
    __table_args__ = (
        # B-tree index on normal column (fastest)
        Index('idx_status', 'status'),
        Index('idx_cpu_temp', 'cpu_temp'),
        
        # GIN index on JSONB (flexible queries)
        Index('idx_settings_gin', 'settings', postgresql_using='gin',
              postgresql_ops={'settings': 'jsonb_path_ops'}),
    )
```

**Step 2:** Query efficiently (JSONB Query Guide)
```sql
-- Fast: uses B-tree index on status
SELECT * FROM device_settings
WHERE status = 'active' AND cpu_temp > 80;

-- Fast: uses GIN index on settings
SELECT * FROM device_settings
WHERE settings @> '{"config": {"fan_profile": "quiet"}}';

-- Combine both for optimal performance
SELECT * FROM device_settings
WHERE status = 'active'
  AND cpu_temp > 80
  AND settings @@ '$.config.fan_profile == "quiet"';
```

---

### Example 3: Complete Omega Control Panel Flow

**Step 1:** Initial Schema Setup (Flask-Migrate Guide)
```bash
# Initialize migrations
flask db init

# Create initial migration
flask db migrate -m "Initial schema: users, roles, device_settings"

# Review and edit migration file

# Apply migration
flask db upgrade
```

**Step 2:** Add JSONB Indexes (Flask-Migrate Guide)
```bash
# Create migration for indexes
flask db migrate -m "Add JSONB indexes for performance"

# Edit migration to add GIN indexes

# Apply migration
flask db upgrade
```

**Step 3:** Query Device Data (JSONB Query Guide)
```python
# In Flask-SQLAlchemy model or view
from sqlalchemy import func, text

# Get critical alerts for dashboard
critical_alerts = db.session.execute(
    text("""
        SELECT 
            ds.device_id,
            jsonb_path_query(
                ds.data,
                '$.alerts[*] ? (@.severity >= 7 && @.timestamp >= $since)',
                jsonb_build_object(
                    'since', to_char(current_timestamp - interval '24 hours', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
                )
            ) AS alerts
        FROM device_settings ds
        WHERE ds.data @@ '$.status == "active"'
    """)
).fetchall()
```

**Step 4:** Update Schema as Needed (Flask-Migrate Guide)
```bash
# Modify model (e.g., add new column)
# ...

# Create migration
flask db migrate -m "Add last_updated column to device_settings"

# Review migration

# Apply migration
flask db upgrade
```

---

## Best Practices for Combined Usage

### 1. Start with Schema (Flask-Migrate Guide)

- Design your models first
- Use normal columns for frequently queried fields
- Use JSONB for flexible/variable data
- Add indexes via migrations (not directly in code)

### 2. Optimize Queries (JSONB Query Guide)

- Use GIN indexes for JSONB containment queries
- Use expression indexes for specific paths
- Use LATERAL joins for array unnesting
- Use variables for dynamic queries (safer + faster)

### 3. Iterate and Improve

- Add indexes based on query patterns
- Monitor query performance
- Adjust schema as needed (via migrations)
- Update query patterns as requirements evolve

---

## Quick Reference: When to Use Which Guide

| Task | Guide | Section |
|------|-------|---------|
| Set up Flask-Migrate | Flask-Migrate | Installation, Configuration |
| Create database models | Flask-Migrate | Database Schema, Implementation Plan |
| Create initial migration | Flask-Migrate | Commands Reference |
| Add/modify columns | Flask-Migrate | Real-World Examples |
| Add JSONB indexes | Flask-Migrate | (migration file) + JSONB Query Guide | Indexing Strategies |
| Query JSONB data | JSONB Query | Core JSONB Operators, JSONPath Basics |
| Filter JSONB arrays | JSONB Query | LATERAL Joins, Time-Based Filtering |
| Aggregate JSONB data | JSONB Query | Arrays & Aggregation |
| Optimize query performance | JSONB Query | Indexing Strategies |
| Troubleshoot migrations | Flask-Migrate | Troubleshooting Common Migration Errors |
| Advanced JSONPath queries | JSONB Query | Variables & Parameterization, Top-N Queries |

---

## Status

✅ **Integration Complete** — Both guides work seamlessly together  
✅ **Cross-Referenced** — Each guide links to the other  
✅ **Production-Ready** — Comprehensive coverage of migrations + querying  
✅ **Omega-Optimized** — Real-world examples for Omega Control Panel

---

## Related Documentation

- [Flask-Migrate Setup Guide](./FLASK_MIGRATE_SETUP.md) — Schema management and migrations
- [PostgreSQL JSONB Query Guide](./POSTGRESQL_JSONB_QUERY_GUIDE.md) — Advanced querying and optimization
- Flask-SQLAlchemy Documentation — ORM integration
- PostgreSQL JSONB Documentation — Official JSONB reference

---

**Last Updated:** January 2026  
**Version:** 1.0  
**Status:** Complete & Production-Ready
