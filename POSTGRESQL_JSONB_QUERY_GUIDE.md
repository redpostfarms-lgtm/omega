# PostgreSQL JSONB Query Guide for Omega Control Panel

**Date:** January 2026  
**Developer:** Nick (Seattle)  
**Status:** Production-Ready  
**Integration:** Works hand-in-hand with [Flask-Migrate Setup Guide](./FLASK_MIGRATE_SETUP.md)

---

## Overview

This guide provides comprehensive PostgreSQL JSONB querying techniques for the Omega Control Panel project. It covers JSONPath operators, LATERAL joins, aggregation, time-based filtering, and advanced patterns — all optimized for hardware monitoring, alerts, and device configuration management.

**Integration Note:** This guide works seamlessly with the Flask-Migrate setup. Use Flask-Migrate for schema management (migrations), and JSONB queries (this guide) for flexible, performant data querying.

---

## Table of Contents

1. [Core JSONB Operators](#core-jsonb-operators)
2. [JSONPath Basics](#jsonpath-basics)
3. [Variables & Parameterization](#variables--parameterization)
4. [Arrays & Aggregation](#arrays--aggregation)
5. [LATERAL Joins](#lateral-joins)
6. [Time-Based Filtering](#time-based-filtering)
7. [Top-N Queries](#top-n-queries)
8. [Grouping & Analytics](#grouping--analytics)
9. [Indexing Strategies](#indexing-strategies)
10. [Omega Control Panel Use Cases](#omega-control-panel-use-cases)

---

## Prerequisites

- PostgreSQL 12+ (JSONPath support)
- PostgreSQL 15+ recommended (enhanced JSONPath features)
- Flask-SQLAlchemy setup (see [Flask-Migrate Setup Guide](./FLASK_MIGRATE_SETUP.md))
- Understanding of JSONB data type

---

## Core JSONB Operators

### Essential Operators Reference

| Operator | Returns | Use Case | Example |
| ---------- | --------- | ---------- | --------- |
| `->` | JSONB | Get object/array by key | `data -> 'config'` |
| `->>` | TEXT | Get value as string | `data ->> 'status'` |
| `#>` | JSONB | Get nested path (array keys) | `data #> '{user,address,city}'` |
| `#>>` | TEXT | Nested path as text | `data #>> '{user,address,city}'` |
| `@>` | boolean | Containment (left contains right) | `data @> '{"status": "active"}'` |
| `?` | boolean | Key exists at top level | `data ? 'error_code'` |
| `?\|` `?&` | boolean | Any/all keys exist | `data ?\| array['a', 'b']` |
| `@?` `@@` | boolean | SQL/JSON path match (PostgreSQL 12+) | `data @@ '$.priority > 5'` |

### Basic Examples (Omega Device Context)

```sql
-- Example table structure (created via Flask-Migrate)
CREATE TABLE device_settings (
    id          SERIAL PRIMARY KEY,
    device_id   TEXT NOT NULL UNIQUE,
    data        JSONB NOT NULL DEFAULT '{}',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example JSONB document
{
  "device_id": "OMEGA-001",
  "status": "active",
  "config": {
    "fan_profile": "quiet",
    "max_temp": 85,
    "rgb": {"enabled": true, "mode": "rainbow", "speed": 4}
  },
  "alerts": [
    {"type": "temp", "severity": 8, "timestamp": "2026-01-10T14:30:00Z"},
    {"type": "fan", "severity": 3, "timestamp": "2026-01-10T13:15:00Z"}
  ]
}
```text

```sql
-- Exact match on a field (fast with index)
SELECT id, data ->> 'device_id' AS device_id
FROM device_settings
WHERE data ->> 'status' = 'active';

-- Using containment (great for partial matches)
SELECT *
FROM device_settings
WHERE data @> '{"status": "active", "config": {"fan_profile": "quiet"}}';

-- Check if key exists
SELECT id
FROM device_settings
WHERE data ? 'alerts';
```text

---

## JSONPath Basics

### JSONPath Operators (PostgreSQL 12+)

| Operator | Meaning | Example |
| ---------- | --------- | --------- |
| `$` | Root | `$.config` |
| `.key` | Object member | `$.config.fan_profile` |
| `[*]` | Array elements | `$.alerts[*]` |
| `?()` | Filter expression | `$.alerts[*] ? (@.severity >= 7)` |
| `@` | Current context (in filters) | `@.severity` |
| `.*` | All keys at level | `$.config.*` |
| `[last]` | Last array element | `$.alerts[last]` |

### Basic JSONPath Examples

```sql
-- Simple path navigation
WHERE data @@ '$.config.fan_profile == "quiet"'

-- Numeric comparison
WHERE data @@ '$.config.max_temp > 80'

-- String starts with
WHERE data @@ '$.alerts[*].message starts with "CPU"'

-- Check if path exists
WHERE data @? '$.alerts'

-- Array element access
WHERE data @@ '$.alerts[0].severity >= 7'
```text

### Filter Expressions

```sql
-- Basic single-condition filter
SELECT jsonb_path_query(data, '$.alerts[*] ? (@.severity >= 6)')
FROM device_settings;

-- Multiple conditions with AND
SELECT jsonb_path_query(
    data,
    '$.alerts[*] ? (@.type == "temp" && @.severity >= 7)'
)
FROM device_settings;

-- OR condition
WHERE data @@ '$.config.fan_profile == "quiet" || $.config.fan_profile == "balanced"'

-- Using IN for membership
WHERE data @@ '$.config.fan_profile in ("quiet", "balanced", "eco")'
```text

### Supported Filter Operators & Functions

| Category | Operators/Functions | Example |
| ---------- | --------------------- | --------- |
| Comparison | `==`, `!=`, `>`, `>=`, `<`, `<=` | `@.severity > 5` |
| Logical | `&&` (AND), `\|\|` (OR) | `@.type == "temp" && @.severity >= 7` |
| Membership | `in (value, ...)` | `@.profile in ("quiet", "balanced")` |
| String | `starts with`, `ends with`, `contains`, `like_regex` | `@.message starts with "CPU"` |
| Existence | `exists(path)` | `exists(@.details)` |
| Size/Count | `size()` (array length or object key count) | `size(@.alerts) > 3` |
| Type Checks | `@ is boolean`, `@ is number`, `@ is string` | `@.enabled is boolean` |
| Arithmetic | `+`, `-`, `*`, `/`, `%`, `abs()`, `floor()`, `ceiling()` | `@.value * 1.1 > 100` |

---

## Variables & Parameterization

Using variables in PostgreSQL JSONPath (also called parameterized JSONPath or named bind variables) is the recommended, safe way to make your JSONPath expressions dynamic without risking SQL injection or messy string concatenation.

### Key Functions That Support Variables

All JSONPath-related functions accept an optional `vars` parameter (type jsonb):

- `jsonb_path_exists(target jsonb, path jsonpath [, vars jsonb [, silent bool]])`
- `jsonb_path_match(...)` → for `@@` operator logic
- `jsonb_path_query(...)` → returns set of matching jsonb items
- `jsonb_path_query_array(...)` → same but as single JSONB array
- `jsonb_path_query_first(...)` → first match only

### Basic Variable Examples

```sql
-- Filter by dynamic severity threshold
SELECT id, device_id
FROM device_settings
WHERE jsonb_path_exists(
    data,
    '$.alerts[*] ? (@.severity >= $min_sev)',
    '{"min_sev": 7}'::jsonb
);

-- Multiple variables – clean and type-safe
SELECT id,
       jsonb_path_query(
           data,
           '$.alerts[*] ? (
               @.type == $alert_type 
               && @.severity >= $min_severity
               && @.timestamp >= $since_date
           )',
           jsonb_build_object(
               'alert_type', 'temp'::text,
               'min_severity', 6::int,
               'since_date', '2026-01-01T00:00:00Z'::text
           )
       ) AS recent_critical_alerts
FROM device_settings;
```text

### Variables with Arrays

```sql
-- Check if fan_profile is in a dynamic list
WHERE jsonb_path_exists(
    data,
    '$.config.fan_profile in ($profile1, $profile2, $profile3)',
    jsonb_build_object(
        'profile1', 'quiet'::text,
        'profile2', 'balanced'::text,
        'profile3', 'eco'::text
    )
);

-- Dynamic key access (very useful for metrics)
SELECT jsonb_path_query_first(
    data,
    '$.metrics.last_hour.$metric_name',
    '{"metric_name": "avg_temp"}'::jsonb
) AS last_hour_avg_temp
FROM device_settings;
```text

### Variables with Array Size Checks

```sql
-- Devices with more alerts than a user-defined threshold
WHERE jsonb_path_exists(
    data,
    'size($.alerts) > $min_alerts',
    '{"min_alerts": 5}'::jsonb
);

-- At least N critical alerts
WHERE jsonb_path_exists(
    data,
    'size($.alerts ? (@.severity >= 7)) >= $critical_count',
    '{"critical_count": 2}'::jsonb
);

-- Range check (between min and max)
WHERE jsonb_path_exists(
    data,
    'size($.alerts) >= $min && size($.alerts) <= $max',
    jsonb_build_object('min', 2, 'max', 10)
);
```text

### Best Practices for Variables (2026)

1. **Always use `vars` instead of string concatenation** → much safer and more performant
2. **Use `jsonb_build_object()` for dynamic values** from SQL expressions
3. **For large/complex vars** → build once and reuse
4. **Index strategy** → GIN with `jsonb_path_ops` still works great with variables
5. **`silent => true`** → useful in production to suppress errors

---

## Arrays & Aggregation

PostgreSQL's SQL/JSON Path language has limited built-in aggregation functions. The only aggregation-like function natively supported is:

- **`size()`** — returns the number of elements in an array (or number of keys in an object)

### Using size()

```sql
-- Number of alerts
SELECT jsonb_path_query_first(data, 'size($.alerts)') AS alert_count
FROM device_settings;

-- Number of high-severity alerts (filtered)
SELECT jsonb_path_query_first(
    data,
    'size($.alerts ? (@.severity >= 7))'
) AS critical_count
FROM device_settings;
```text

### Aggregation via SQL Functions

Since `jsonb_path_query()` returns a set of jsonb values (one row per matching item), use standard PostgreSQL aggregate functions:

```sql
-- Sum of all alert severities
SELECT sum((value ->> 'severity')::int) AS total_severity
FROM device_settings,
     jsonb_path_query(data, '$.alerts[*].severity') AS value;

-- Average CPU temperature threshold
SELECT avg((value ->> 'cpu')::numeric) AS avg_cpu_threshold
FROM device_settings,
     jsonb_path_query(data, '$.config.alert_thresholds.cpu') AS value;

-- Count of critical alerts (severity >= 7) per device
SELECT 
    device_id,
    count(*) AS critical_count
FROM device_settings,
     jsonb_path_query(data, '$.alerts[*] ? (@.severity >= 7)') AS alert
GROUP BY device_id;

-- Collect all unique alert types into an array
SELECT 
    device_id,
    array_agg(DISTINCT value ->> 'type') AS alert_types
FROM device_settings,
     jsonb_path_query(data, '$.alerts[*].type') AS value
GROUP BY device_id;
```text

---

## LATERAL Joins

LATERAL joins with JSONPath are one of the most powerful patterns in PostgreSQL when you need to:

- Extract multiple values from a JSONB array/object
- Apply aggregates, filters, or transformations on those extracted values
- Join the results back to the parent row in a clean, performant way

### Basic Pattern

```sql
SELECT 
    ds.device_id,
    alert.value AS alert_json,
    (alert.value ->> 'severity')::int AS severity,
    alert.value ->> 'type' AS alert_type
FROM device_settings ds
CROSS JOIN LATERAL jsonb_path_query(
    ds.data,
    '$.alerts[*]'
) AS alert(value);
```text

This is equivalent to: "for each device, unnest all its alerts into separate rows"

### Real-World Examples

```sql
-- Unnest alerts + filter high-severity only
SELECT 
    ds.device_id,
    alert.value ->> 'type' AS type,
    (alert.value ->> 'severity')::int AS severity
FROM device_settings ds
CROSS JOIN LATERAL jsonb_path_query(
    ds.data,
    '$.alerts[*] ? (@.severity >= 6)'
) AS alert(value)
ORDER BY severity DESC;

-- Aggregate per device using LATERAL + GROUP BY
SELECT 
    ds.device_id,
    count(*) AS total_alerts,
    avg((alert.value ->> 'severity')::int) AS avg_severity,
    max((alert.value ->> 'severity')::int) AS max_severity
FROM device_settings ds
CROSS JOIN LATERAL jsonb_path_query(
    ds.data,
    '$.alerts[*]'
) AS alert(value)
GROUP BY ds.device_id;

-- Using variables in JSONPath + LATERAL
SELECT 
    ds.device_id,
    alert.value ->> 'type' AS type,
    (alert.value ->> 'severity')::int AS severity
FROM device_settings ds
CROSS JOIN LATERAL jsonb_path_query(
    ds.data,
    '$.alerts[*] ? (@.severity >= $min_sev && @.type = $alert_type)',
    jsonb_build_object('min_sev', 7, 'alert_type', 'temp')
) AS alert(value);
```text

### CROSS JOIN LATERAL vs LEFT JOIN LATERAL

| Use Case | Join Type | Result when no matches |
| ---------- | ----------- | ------------------------ |
| Only want rows that have alerts | `CROSS JOIN LATERAL` | Device disappears if no alerts |
| Want all devices (even zero alerts) | `LEFT JOIN LATERAL` | Device stays, extracted fields = NULL/0 |

---

## Time-Based Filtering

Filtering alerts based on timestamp ranges (last X hours/days) is common in monitoring systems.

### Last X Hours Example

```sql
-- Last 24 hours
SELECT 
    ds.device_id,
    t.alert_json,
    t.alert_type,
    t.severity,
    t.timestamp,
    t.rn
FROM device_settings ds
CROSS JOIN LATERAL (
    SELECT 
        value AS alert_json,
        value ->> 'type'        AS alert_type,
        (value ->> 'severity')::int AS severity,
        value ->> 'timestamp'   AS timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY ds.device_id 
            ORDER BY value ->> 'timestamp' DESC
        ) AS rn
    FROM jsonb_path_query(
        ds.data,
        '$.alerts[*] ? (@.timestamp >= $since_time)',
        jsonb_build_object(
            'since_time', 
            to_char(current_timestamp - interval '24 hours', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
        )
    )
) t
ORDER BY ds.device_id, t.rn;
```text

### Last X Days Example

```sql
-- Last 7 days
WITH recent_alerts AS (
    SELECT 
        ds.device_id,
        value AS alert_json,
        to_timestamp(value ->> 'timestamp', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') 
            AT TIME ZONE 'America/Denver' AS alert_time_mst
    FROM device_settings ds
    CROSS JOIN LATERAL jsonb_path_query(
        ds.data,
        '$.alerts[*] ? (@.timestamp >= $since)',
        jsonb_build_object(
            'since', to_char(
                current_timestamp AT TIME ZONE 'America/Denver' - interval '7 days',
                'YYYY-MM-DD"T"00:00:00"Z"'
            )
        )
    ) AS value
)
SELECT 
    device_id,
    date_trunc('day', alert_time_mst) AS day_mst,
    count(*) AS daily_alert_count,
    jsonb_agg(alert_json ORDER BY alert_time_mst DESC) AS all_alerts_that_day
FROM recent_alerts
GROUP BY device_id, date_trunc('day', alert_time_mst)
ORDER BY device_id, day_mst DESC;
```text

### Timezone Handling

```sql
-- For MST (UTC-7) timezone
current_timestamp AT TIME ZONE 'America/Denver'

-- For UTC (remove AT TIME ZONE part)
current_timestamp

-- For other timezones
current_timestamp AT TIME ZONE 'America/New_York'
current_timestamp AT TIME ZONE 'Europe/London'
```text

---

## Top-N Queries

### Top N Highest Severity Alerts per Device

```sql
SELECT 
    ds.device_id,
    t.alert_json,
    t.severity,
    t.alert_type,
    t.timestamp,
    t.rn          -- rank within device
FROM device_settings ds
CROSS JOIN LATERAL (
    SELECT 
        value AS alert_json,
        (value ->> 'severity')::int AS severity,
        value ->> 'type'        AS alert_type,
        value ->> 'timestamp'   AS timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY ds.device_id 
            ORDER BY (value ->> 'severity')::int DESC, 
                     value ->> 'timestamp' DESC   -- tiebreaker: most recent first
        ) AS rn
    FROM jsonb_path_query(ds.data, '$.alerts[*]')
) t
WHERE t.rn <= 3   -- Top 3
ORDER BY ds.device_id, t.rn;
```text

### Top N as Aggregated JSON Array per Device

```sql
SELECT 
    ds.device_id,
    jsonb_agg(t.alert_json ORDER BY t.severity DESC, t.timestamp DESC) AS top_alerts
FROM device_settings ds
CROSS JOIN LATERAL (
    SELECT 
        value AS alert_json,
        (value ->> 'severity')::int AS severity,
        value ->> 'timestamp'   AS timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY ds.device_id 
            ORDER BY (value ->> 'severity')::int DESC, 
                     value ->> 'timestamp' DESC
        ) AS rn
    FROM jsonb_path_query(ds.data, '$.alerts[*]')
) t
WHERE t.rn <= 3
GROUP BY ds.device_id;
```text

### Top N Most Recent Alerts per Device

```sql
SELECT 
    ds.device_id,
    t.alert_json,
    t.timestamp,
    t.rn               -- rank (1 = most recent)
FROM device_settings ds
CROSS JOIN LATERAL (
    SELECT 
        value AS alert_json,
        value ->> 'timestamp'   AS timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY ds.device_id
            ORDER BY value ->> 'timestamp' DESC   -- most recent first
        ) AS rn
    FROM jsonb_path_query(ds.data, '$.alerts[*]')
) t
WHERE t.rn <= 5          -- Top 5 most recent
ORDER BY ds.device_id, t.rn;
```text

### Top N per Alert Type per Device

```sql
SELECT 
    ds.device_id,
    t.alert_type,
    t.severity,
    t.timestamp,
    t.rn_in_type          -- rank within the same type per device
FROM device_settings ds
CROSS JOIN LATERAL (
    SELECT 
        value AS alert_json,
        value ->> 'type'        AS alert_type,
        (value ->> 'severity')::int AS severity,
        value ->> 'timestamp'   AS timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY ds.device_id, (value ->> 'type')
            ORDER BY (value ->> 'severity')::int DESC,
                     value ->> 'timestamp' DESC
        ) AS rn_in_type
    FROM jsonb_path_query(ds.data, '$.alerts[*]')
) t
WHERE t.rn_in_type <= 3   -- Top 3 per type
ORDER BY ds.device_id, t.alert_type, t.rn_in_type;
```text

---

## Grouping & Analytics

### Count per Type within Each Hour

```sql
WITH recent_alerts AS (
    SELECT 
        ds.device_id,
        value ->> 'type' AS alert_type,
        to_timestamp(value ->> 'timestamp', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') 
            AT TIME ZONE 'America/Denver' AS alert_time_mst
    FROM device_settings ds
    CROSS JOIN LATERAL jsonb_path_query(
        ds.data,
        '$.alerts[*] ? (@.timestamp >= $since)',
        jsonb_build_object(
            'since', to_char(
                current_timestamp AT TIME ZONE 'America/Denver' - interval '48 hours',
                'YYYY-MM-DD"T"HH24:MI:SS"Z"'
            )
        )
    ) AS value
)
SELECT 
    device_id,
    date_trunc('hour', alert_time_mst) AS hour_mst,
    alert_type,
    count(*) AS count_per_type_hour
FROM recent_alerts
GROUP BY device_id, date_trunc('hour', alert_time_mst), alert_type
ORDER BY device_id, hour_mst DESC, count_per_type_hour DESC;
```text

### Count per Type within Each Day

```sql
WITH recent_alerts AS (
    SELECT 
        ds.device_id,
        value ->> 'type' AS alert_type,
        to_timestamp(value ->> 'timestamp', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') 
            AT TIME ZONE 'America/Denver' AS alert_time_mst
    FROM device_settings ds
    CROSS JOIN LATERAL jsonb_path_query(
        ds.data,
        '$.alerts[*] ? (@.timestamp >= $since)',
        jsonb_build_object(
            'since', to_char(
                current_timestamp AT TIME ZONE 'America/Denver' - interval '7 days',
                'YYYY-MM-DD"T"00:00:00"Z"'
            )
        )
    ) AS value
)
SELECT 
    device_id,
    date_trunc('day', alert_time_mst) AS day_mst,
    alert_type,
    count(*) AS count_per_type_day
FROM recent_alerts
GROUP BY device_id, date_trunc('day', alert_time_mst), alert_type
ORDER BY device_id, day_mst DESC, count_per_type_day DESC;
```text

### Pivot-Style: One Column per Type (Dashboards)

```sql
SELECT 
    device_id,
    date_trunc('hour', alert_time_mst) AS hour_mst,
    count(*) FILTER (WHERE alert_type = 'temp')     AS temp_count,
    count(*) FILTER (WHERE alert_type = 'fan')      AS fan_count,
    count(*) FILTER (WHERE alert_type = 'voltage')  AS voltage_count,
    count(*) FILTER (WHERE alert_type NOT IN ('temp','fan','voltage')) AS other_count
FROM device_settings ds
CROSS JOIN LATERAL (
    SELECT 
        value ->> 'type' AS alert_type,
        to_timestamp(value ->> 'timestamp', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') 
            AT TIME ZONE 'America/Denver' AS alert_time_mst
    FROM jsonb_path_query(
        ds.data,
        '$.alerts[*] ? (@.timestamp >= $since)',
        jsonb_build_object(
            'since', to_char(
                current_timestamp AT TIME ZONE 'America/Denver' - interval '48 hours',
                'YYYY-MM-DD"T"HH24:MI:SS"Z"'
            )
        )
    )
) t
GROUP BY device_id, date_trunc('hour', alert_time_mst)
ORDER BY device_id, hour_mst DESC;
```text

---

## Indexing Strategies

Indexing is critical for JSONB query performance. Match the index type to your actual query patterns.

### Main Index Types for JSONB

| Index Type | Best For | Supported Operators | Size & Write Cost | When to Prefer |
| ------------ | ---------- | --------------------- | ------------------- | ---------------- |
| **GIN (jsonb_ops)** | General-purpose: containment (@>), key existence (?), path queries | @>, ?, ?, ?&, @?, @@ | Larger (60–80% of table size), slower writes | Need key existence (?) |
| **GIN (jsonb_path_ops)** | Pure containment + path queries | @>, @?, @@ | Much smaller (20–50% of default), faster writes | Only containment/path, frequent common keys |
| **Expression B-tree** | Exact match on specific path/value | =, <, >, BETWEEN, ORDER BY | Small | Fixed, high-frequency paths |
| **Partial Index** | Subset of data | Any above + WHERE clause | Very small | Selective queries on subset |

### Recommended Strategy: Hybrid Approach

```sql
-- Hybrid schema example
CREATE TABLE device_settings (
    id           SERIAL PRIMARY KEY,
    device_id    TEXT NOT NULL,
    status       TEXT,                    -- ← normal column + index
    cpu_temp     NUMERIC,                 -- ← normal for fast range
    settings     JSONB NOT NULL DEFAULT '{}',
    
    -- Normal columns with B-tree indexes (fastest for frequent paths)
    INDEX idx_status_btree (status),
    INDEX idx_cpu_temp_btree (cpu_temp),
    
    -- GIN for flexible JSONB queries
    INDEX idx_settings_gin USING GIN (settings jsonb_path_ops)  -- containment only
);
```text

### When to Choose jsonb_ops vs jsonb_path_ops

- **Use `jsonb_ops` (default)** if you need key existence (`?`, `?|`, `?&`)
- **Use `jsonb_path_ops` (recommended for most)** when you only do:
  - Containment (`@>`)
  - JSONPath matches (`@?`, `@@`)
  - → 20–50% smaller index + better performance on common keys

```sql
-- Smaller & faster for containment
CREATE INDEX idx_settings_path_ops
ON device_settings USING GIN (settings jsonb_path_ops);
```text

### Expression Indexes for Specific Paths

```sql
-- Fast exact match / range on nested value
CREATE INDEX idx_fan_mode_btree
ON device_settings ((settings ->> 'fan_profile')) WHERE status = 'active';

-- Fast containment inside a known nested object
CREATE INDEX idx_rgb_modes_gin
ON device_settings USING GIN ((settings -> 'rgb'));
```text

### Performance Trade-offs Summary (2025–2026 Benchmarks)

- **Full GIN (jsonb_ops)** → write penalty 2–5× higher than B-tree, index can be huge
- **jsonb_path_ops** → significantly smaller + faster for @>/@@
- **Expression B-tree** → fastest lookup/sort when path is known & fixed (often 5–20× faster than GIN for equals)
- **GIN + B-tree combo** → best of both worlds for mixed workloads

### Quick Decision Flowchart

```text
Do you query mostly fixed paths (status, temp, fan_speed)?
   ↓ Yes → Expression B-tree / normal columns
   ↓ No / variable structure → GIN

Need key existence (?) ?
   ↓ Yes → jsonb_ops
   ↓ Only @>, @?, @@ → jsonb_path_ops (smaller + faster)

Very large table + infrequent writes?
   → GIN is fine

Frequent updates to large JSONB objects?
   → Minimize JSONB size + use expression indexes + partial indexes
```text

---

## Omega Control Panel Use Cases

### Use Case 1: Device Status Dashboard

**Goal:** Show all active devices with their current configuration and alert counts.

```sql
SELECT 
    device_id,
    data ->> 'status' AS status,
    data -> 'config' ->> 'fan_profile' AS fan_profile,
    jsonb_path_query_first(data, 'size($.alerts)')::int AS total_alerts,
    jsonb_path_query_first(data, 'size($.alerts ? (@.severity >= 7))')::int AS critical_alerts
FROM device_settings
WHERE data ->> 'status' = 'active'
ORDER BY critical_alerts DESC, total_alerts DESC;
```text

### Use Case 2: Critical Alert Monitoring

**Goal:** Find all devices with critical temperature alerts in the last 24 hours.

```sql
SELECT 
    ds.device_id,
    alert.value ->> 'type' AS alert_type,
    (alert.value ->> 'severity')::int AS severity,
    alert.value ->> 'timestamp' AS timestamp,
    alert.value ->> 'message' AS message
FROM device_settings ds
CROSS JOIN LATERAL jsonb_path_query(
    ds.data,
    '$.alerts[*] ? (
        @.type == "temp" 
        && @.severity >= 7 
        && @.timestamp >= $since_time
    )',
    jsonb_build_object(
        'since_time',
        to_char(current_timestamp - interval '24 hours', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
    )
) AS alert(value)
ORDER BY severity DESC, timestamp DESC;
```text

### Use Case 3: Configuration Compliance Check

**Goal:** Find devices that don't have required configuration settings.

```sql
SELECT 
    device_id,
    data -> 'config' AS current_config
FROM device_settings
WHERE NOT (
    data @> '{"config": {"fan_profile": {}}}'
    AND data @> '{"config": {"max_temp": {}}}'
    AND data @> '{"config": {"rgb": {"enabled": true}}}'
);
```text

### Use Case 4: Hourly Alert Summary (Dashboard Chart Data)

**Goal:** Get alert counts per type per hour for the last 48 hours (ready for Chart.js).

```sql
WITH recent_alerts AS (
    SELECT 
        ds.device_id,
        value ->> 'type' AS alert_type,
        to_timestamp(value ->> 'timestamp', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') 
            AT TIME ZONE 'America/Denver' AS alert_time_mst
    FROM device_settings ds
    CROSS JOIN LATERAL jsonb_path_query(
        ds.data,
        '$.alerts[*] ? (@.timestamp >= $since)',
        jsonb_build_object(
            'since', to_char(
                current_timestamp AT TIME ZONE 'America/Denver' - interval '48 hours',
                'YYYY-MM-DD"T"HH24:MI:SS"Z"'
            )
        )
    ) AS value
)
SELECT 
    device_id,
    date_trunc('hour', alert_time_mst) AS hour_mst,
    count(*) FILTER (WHERE alert_type = 'temp')     AS temp_count,
    count(*) FILTER (WHERE alert_type = 'fan')      AS fan_count,
    count(*) FILTER (WHERE alert_type = 'voltage')  AS voltage_count,
    count(*) AS total_count
FROM recent_alerts
GROUP BY device_id, date_trunc('hour', alert_time_mst)
ORDER BY device_id, hour_mst DESC;
```text

### Use Case 5: Top 5 Most Critical Devices

**Goal:** Rank devices by number of critical alerts in the last 7 days.

```sql
SELECT 
    ds.device_id,
    count(*) AS critical_alert_count,
    max((alert.value ->> 'severity')::int) AS max_severity,
    jsonb_agg(alert.value ORDER BY (alert.value ->> 'severity')::int DESC) 
        FILTER (WHERE row_number() OVER (PARTITION BY ds.device_id ORDER BY (alert.value ->> 'severity')::int DESC) <= 3)
        AS top_3_alerts
FROM device_settings ds
CROSS JOIN LATERAL jsonb_path_query(
    ds.data,
    '$.alerts[*] ? (@.severity >= 7 && @.timestamp >= $since)',
    jsonb_build_object(
        'since', to_char(current_timestamp - interval '7 days', 'YYYY-MM-DD"T"00:00:00"Z"')
    )
) AS alert(value)
GROUP BY ds.device_id
ORDER BY critical_alert_count DESC, max_severity DESC
LIMIT 5;
```text

---

## Integration with Flask-Migrate

This guide works seamlessly with the [Flask-Migrate Setup Guide](./FLASK_MIGRATE_SETUP.md):

1. **Schema Management** (Flask-Migrate):
   - Create tables with JSONB columns
   - Add/modify columns over time
   - Manage database schema versioning

2. **Query Optimization** (This Guide):
   - Add GIN indexes on JSONB columns (via migrations)
   - Add expression indexes on frequent paths (via migrations)
   - Use these query patterns in your Flask-SQLAlchemy models

### Example Migration: Adding JSONB Index

```python
# migrations/versions/xxxx_add_jsonb_indexes.py
def upgrade():
    op.create_index(
        'idx_device_settings_data_gin',
        'device_settings',
        ['data'],
        postgresql_using='gin',
        postgresql_ops={'data': 'jsonb_path_ops'}
    )
    
    op.create_index(
        'idx_device_settings_fan_profile',
        'device_settings',
        [sa.text("(data->'config'->>'fan_profile')")],
        postgresql_where=sa.text("data->>'status' = 'active'")
    )
```text

### Example Flask-SQLAlchemy Model

```python
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, text

db = SQLAlchemy()

class DeviceSettings(db.Model):
    __tablename__ = 'device_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(80), unique=True, nullable=False)
    data = db.Column(db.JSON, nullable=False, default={})
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Indexes (created via migrations)
    __table_args__ = (
        Index('idx_data_gin', 'data', postgresql_using='gin', 
              postgresql_ops={'data': 'jsonb_path_ops'}),
        Index('idx_fan_profile', text("(data->'config'->>'fan_profile')")),
    )
    
    @property
    def alert_count(self):
        """Get total alert count using JSONPath."""
        from sqlalchemy import func
        result = db.session.execute(
            func.jsonb_path_query_first(
                self.data,
                'size($.alerts)'
            )
        )
        return result.scalar() or 0
```text

---

## Best Practices Summary (2026)

1. **Use `jsonb_path_ops` GIN index** unless you need key existence (`?`)
2. **Hybrid indexing** → normal columns + B-tree for hot paths, GIN for flexible parts
3. **Use variables** (`vars` parameter) for dynamic queries → safer + more performant
4. **Keep JSONB objects small** (<2KB per value) → avoid TOAST overhead
5. **LATERAL joins** → powerful for unnesting arrays and aggregating
6. **Test on staging** → JSONB indexes can be large, test performance first
7. **Combine with Flask-Migrate** → manage schema + indexes via migrations

---

## Quick Reference Cheat Sheet

### Most Common Patterns

```sql
-- Exact match (with expression index)
WHERE data ->> 'status' = 'active'

-- Containment (with GIN index)
WHERE data @> '{"config": {"fan_profile": "quiet"}}'

-- JSONPath match (with GIN index)
WHERE data @@ '$.config.max_temp > 80'

-- Array filtering (with LATERAL)
CROSS JOIN LATERAL jsonb_path_query(data, '$.alerts[*] ? (@.severity >= 7)') AS alert

-- Variables (safe + performant)
jsonb_path_exists(data, '$.alerts[*] ? (@.severity >= $min)', '{"min": 7}'::jsonb)

-- Aggregation
SELECT count(*), avg((value ->> 'severity')::int)
FROM device_settings,
     jsonb_path_query(data, '$.alerts[*]') AS value

-- Time-based filtering
'$.alerts[*] ? (@.timestamp >= $since)'
jsonb_build_object('since', to_char(current_timestamp - interval '24 hours', ...))
```text

---

## Status

✅ **Production-Ready** — Comprehensive guide with real-world examples  
✅ **Integrated** — Works seamlessly with Flask-Migrate setup  
✅ **Optimized** — Indexing strategies and performance tips included  
✅ **Practical** — Omega Control Panel use cases throughout

---

## Related Documentation

- [Flask-Migrate Setup Guide](./FLASK_MIGRATE_SETUP.md) — Database migrations and schema management
- Flask-SQLAlchemy Documentation — ORM integration
- PostgreSQL JSONB Documentation — Official JSONB reference

---

**Last Updated:** January 2026  
**Version:** 1.0  
**Status:** Production-Ready
