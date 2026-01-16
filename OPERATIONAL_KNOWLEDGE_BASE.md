# Operational Knowledge Base - Complete System Guide
**Status:** Complete & Comprehensive  
**Date:** January 16, 2026  
**Purpose:** Production-ready operational knowledge for all systems

---

## Table of Contents

1. [System Monitoring & Health Checks](#system-monitoring--health-checks)
2. [Troubleshooting & Diagnostics](#troubleshooting--diagnostics)
3. [Performance Optimization](#performance-optimization)
4. [Error Handling & Recovery](#error-handling--recovery)
5. [Integration Best Practices](#integration-best-practices)
6. [Deployment & Configuration](#deployment--configuration)
7. [Logging & Metrics](#logging--metrics)
8. [Security Operations](#security-operations)
9. [API Integration Patterns](#api-integration-patterns)
10. [Database Operations](#database-operations)

---

## System Monitoring & Health Checks

### Real-Time Monitoring

**Purpose:** Continuous system health verification

**Key Metrics to Monitor:**
- CPU usage (alert if > 85%)
- Memory usage (alert if > 80%)
- Disk space (alert if < 10% free)
- Network connectivity (ping test every 60s)
- Component health status (HEALTHY, DEGRADED, UNHEALTHY, OFFLINE)
- API response times (alert if > 2000ms)

**Implementation:**
```python
from gatekeeper_error_handler import get_error_handler

handler = get_error_handler()

# Register component
handler.health_monitor.register_component('my_component')

# Check health with automatic status detection
status = handler.health_monitor.check_component_health(
    'my_component',
    lambda: test_component_functionality()
)

# Get comprehensive health report
report = handler.health_monitor.get_health_report()
```

**Health Status Meanings:**
- **HEALTHY**: Component fully operational, all functions working
- **DEGRADED**: Component operational but with reduced functionality
- **UNHEALTHY**: Component not working properly, needs attention
- **OFFLINE**: Component unavailable or unreachable

### Automated Health Checks

**Recommended Check Intervals:**
- System metrics: Every 60 seconds
- Component status: Every 30 seconds
- API availability: Every 5 minutes
- Database connectivity: Every 30 seconds
- Disk space: Every 10 minutes

**Alert Thresholds:**
- Critical: Immediate notification, stop non-essential operations
- Warning: Log and monitor, may need attention
- Info: Log for diagnostics

---

## Troubleshooting & Diagnostics

### Quick Diagnostic Steps

**Step 1: Check System Health**
```python
handler = get_error_handler()
report = handler.health_monitor.get_health_report()
print(f"Overall Status: {report['status']}")
print(f"Healthy Components: {report['healthy_count']}/{report['total_components']}")
```

**Step 2: Review Error Logs**
```python
# Get all errors from recent session
errors = handler.error_history
print(f"Total Errors: {len(errors)}")
for error in errors[-10:]:  # Last 10 errors
    print(f"{error['timestamp']}: {error['severity']} - {error['message']}")
```

**Step 3: Check Integration Status**
```python
# Get integration-specific error report
integration_report = handler.get_integration_error_report()
if integration_report.get('total_integrations_with_errors', 0) > 0:
    print("Integration errors detected:")
    for integration, details in integration_report['integration_errors'].items():
        print(f"  {integration}: {details['error_count']} errors")
```

**Step 4: Validate API Keys**
```python
# Validate integration setup
result = handler.validate_integration_setup(
    'huggingface',
    'hf_abc123def456',
    'huggingface'
)
if not result['ready']:
    print(f"Integration not ready: {result}")
```

### Common Issues & Solutions

#### Issue 1: High Memory Usage
**Symptoms:** Application slows down, memory usage > 80%

**Diagnosis Steps:**
1. Check which components use most memory
2. Review error history for memory-related errors
3. Check for memory leaks in long-running processes

**Solutions:**
- Clear old error history: Deque auto-maintains maxlen=1000
- Reduce cache size in configuration
- Restart components that hold memory
- Profile memory usage with psutil

#### Issue 2: API Integration Failures
**Symptoms:** Integration errors appearing in logs

**Diagnosis Steps:**
1. Check API key validity: `handler.api_key_validator.validate_key_format(key, type)`
2. Test API connection: `handler.api_key_validator.test_api_connection(url, headers)`
3. Review integration error report for specific error type
4. Check rate limiting and connection issues

**Solutions by Error Type:**
- **API_KEY_MISSING**: Run setup process, store key securely
- **API_KEY_INVALID**: Regenerate key from provider dashboard
- **CONNECTION_FAILED**: Check network connectivity, API endpoint status
- **RATE_LIMIT_EXCEEDED**: Implement exponential backoff, reduce request frequency
- **SERVICE_UNAVAILABLE**: Wait for service recovery, use fallback service
- **AUTHENTICATION_FAILED**: Verify key permissions and account status

#### Issue 3: Database Connectivity
**Symptoms:** Database operations fail, connection timeouts

**Diagnosis Steps:**
1. Verify database credentials in configuration
2. Check database service status (running/stopped)
3. Test network connectivity to database server
4. Review connection logs for authentication errors

**Solutions:**
- Verify connection string format is correct
- Check database user permissions
- Ensure database service is running
- Review firewall rules for database port
- Check connection pool exhaustion

#### Issue 4: Slow Performance
**Symptoms:** Operations taking longer than expected

**Diagnosis Steps:**
1. Monitor API response times
2. Check CPU and memory usage
3. Profile code execution times
4. Review database query performance

**Solutions:**
- Implement caching for frequently accessed data
- Optimize database queries with proper indexes
- Reduce API request frequency
- Implement request batching
- Use async/await for I/O operations

---

## Performance Optimization

### Response Time Optimization

**Target Performance Metrics:**
- API calls: < 500ms (p95)
- Database queries: < 100ms (p95)
- File operations: < 200ms (p95)
- Component health checks: < 100ms

**Optimization Techniques:**

1. **Caching Strategy**
   - Cache API responses (TTL: 5-60 minutes based on data volatility)
   - Cache database query results
   - Use in-memory cache for hot data
   - Implement cache invalidation on data update

2. **Query Optimization**
   - Use appropriate indexes on database columns
   - Avoid N+1 queries (use joins)
   - Use LIMIT for result sets
   - Profile slow queries and optimize

3. **Connection Pooling**
   - Use connection pools for database connections
   - Set pool size based on workload (default: 5-20 connections)
   - Monitor pool utilization
   - Close unused connections

4. **Async Operations**
   - Use async/await for I/O operations
   - Process multiple requests concurrently
   - Avoid blocking operations in main thread

### Memory Optimization

**Memory Usage Strategy:**
- Error history: Auto-limited to 1000 entries (~1 MB)
- Health history: Auto-limited to 1000 entries (~500 KB)
- Validation log: Auto-limited to 100 entries (~50 KB)
- Cache size: Configurable based on available memory

**Memory Monitoring:**
```python
import psutil
process = psutil.Process()
memory_info = process.memory_info()
print(f"RSS: {memory_info.rss / 1024 / 1024:.1f} MB")
print(f"VMS: {memory_info.vms / 1024 / 1024:.1f} MB")
```

**Memory Optimization Techniques:**
- Use generators instead of lists for large data
- Delete unused objects explicitly
- Use memory profiling tools to find leaks
- Implement periodic cleanup tasks

---

## Error Handling & Recovery

### Error Handling Hierarchy

**Error Severity Levels (Highest to Lowest Priority):**

1. **FATAL** - System must stop
   - Unrecoverable system errors
   - Critical security breaches
   - Data corruption
   - Action: Log, alert, graceful shutdown

2. **CRITICAL** - Immediate attention required
   - Major component failure
   - Service unavailability
   - Security incidents
   - Action: Log, alert admin, attempt recovery

3. **ERROR** - Operation failed, system still functional
   - API calls failing
   - Database query errors
   - Integration failures
   - Action: Log, retry with backoff, fallback

4. **WARNING** - Degraded functionality
   - Performance degradation
   - Deprecated API usage
   - Unusual patterns
   - Action: Log, monitor, investigate

5. **INFO** - Normal operations
   - Component initialization
   - Normal workflow milestones
   - Performance metrics
   - Action: Log for audit trail

### Recovery Strategies

**Automatic Recovery:**
```python
# Integration-specific recovery with handler
context = ErrorContext('huggingface', 'model_inference', model='bert')
error_info = handler.handle_integration_error(
    'huggingface',
    IntegrationErrorType.RATE_LIMIT_EXCEEDED,
    exception,
    context
)

# Recovery message contains strategy
print(error_info.get('recovery_message'))
# Example: "Rate limited. Implement exponential backoff: wait 2^attempt seconds"
```

**Recovery Strategies by Error Type:**

- **API_KEY_MISSING**: Run setup wizard, prompt for key entry
- **RATE_LIMIT_EXCEEDED**: Wait 2^attempt seconds, exponential backoff
- **CONNECTION_FAILED**: Retry after 5 seconds, use fallback service
- **SERVICE_UNAVAILABLE**: Queue request for retry, notify user
- **AUTHENTICATION_FAILED**: Refresh token, re-authenticate

### Error Reporting

**Generate Comprehensive Error Report:**
```python
# General error report
general_report = handler.get_error_report()

# Integration-specific error report
integration_report = handler.get_integration_error_report()

# Both include:
# - Error counts and types
# - Timestamps
# - Context information
# - Severity levels
# - Recovery strategies
```

---

## Integration Best Practices

### API Integration Checklist

**Before Deploying Integration:**
- [ ] API key stored securely (not in code)
- [ ] API key format validated
- [ ] API connectivity tested
- [ ] Rate limits understood and implemented
- [ ] Error handling for all failure modes
- [ ] Timeout values configured
- [ ] Retry strategy implemented
- [ ] Monitoring/alerting configured

**During Integration Operation:**
- [ ] Monitor API response times
- [ ] Track rate limit consumption
- [ ] Log all API interactions
- [ ] Handle API version changes
- [ ] Update error handling as needed

### Multi-Integration Management

**Managing Multiple Integrations:**
```python
# Register all integrations
integrations = ['huggingface', 'openai', 'nvidia', 'replicate']

for integration in integrations:
    handler.health_monitor.register_component(f'{integration}_integration')
    
    # Validate each integration
    result = handler.validate_integration_setup(
        integration,
        api_key,
        integration
    )
    
    if not result['ready']:
        print(f"Warning: {integration} not ready")
```

**Integration Priority Handling:**
- Prioritize critical integrations for retry
- Use fallback integrations when available
- Load balance across multiple API providers
- Monitor cost per integration

### Dependency Management

**Handling Integration Dependencies:**
- Document dependencies between integrations
- Validate dependent integrations before primary
- Implement fallback chains
- Monitor dependency health

---

## Deployment & Configuration

### Configuration Management

**Configuration File Structure:**
```json
{
  "api_port": 5000,
  "cache_size": 5000,
  "enable_quantum": true,
  "log_level": "INFO",
  "quantum_settings": {
    "enabled": true,
    "optimization_level": 2
  },
  "monitoring": {
    "health_check_interval": 30,
    "alert_thresholds": {
      "cpu": 85,
      "memory": 80,
      "disk": 10
    }
  },
  "integrations": {
    "huggingface": {
      "enabled": true,
      "timeout": 30,
      "retry_attempts": 3
    },
    "openai": {
      "enabled": true,
      "timeout": 30,
      "retry_attempts": 3
    }
  }
}
```

**Configuration Best Practices:**
- Keep configuration separate from code
- Use environment variables for secrets
- Validate configuration on startup
- Document all configuration options
- Version control non-secret configurations

### Deployment Checklist

**Pre-Deployment:**
- [ ] All tests passing
- [ ] No syntax errors (Pylance check)
- [ ] Type hints complete
- [ ] Security review done
- [ ] Configuration validated
- [ ] Backups created
- [ ] Rollback plan ready

**Deployment Steps:**
1. Stop current service
2. Backup current version
3. Deploy new version
4. Validate deployment
5. Run health checks
6. Monitor initial startup
7. Verify all integrations

**Post-Deployment:**
- [ ] Monitor error logs
- [ ] Check performance metrics
- [ ] Validate integrations working
- [ ] User acceptance testing
- [ ] Document any issues

---

## Logging & Metrics

### Comprehensive Logging Strategy

**Log File Locations:**
- `gatekeeper_system.log` - General system operations
- `gatekeeper_errors.log` - Error events
- `gatekeeper_integrations.log` - Integration-specific events

**Log Rotation:**
- Max file size: 5 MB
- Backup count: 5
- Automatic cleanup of old logs

### Metrics Collection

**Key Metrics to Track:**
- Request count and rate
- Response times (min, max, avg, p50, p95, p99)
- Error rate and types
- Cache hit/miss ratio
- API call success rate
- Component health status

**Metrics Storage:**
```python
# Example metrics structure
metrics = {
    'timestamp': datetime.now().isoformat(),
    'request_count': 1000,
    'avg_response_time_ms': 250,
    'error_rate': 0.02,
    'cache_hit_ratio': 0.85,
    'component_health': {
        'huggingface': 'HEALTHY',
        'openai': 'HEALTHY',
        'database': 'HEALTHY'
    }
}
```

### Performance Reporting

**Generate Performance Report:**
```python
# Collect metrics
health_report = handler.health_monitor.get_health_report()
error_report = handler.get_error_report()

# Analyze
avg_errors_per_hour = len(error_report.get('errors', [])) / hours_elapsed
error_rate = avg_errors_per_hour / total_requests_per_hour

# Report
print(f"Error Rate: {error_rate:.2%}")
print(f"Health Status: {health_report['status']}")
```

---

## Security Operations

### API Key Security

**Storage Best Practices:**
- Never store keys in code or version control
- Use environment variables for sensitive data
- Use secure vaults for production
- Rotate keys regularly (quarterly minimum)
- Different keys for dev/staging/production

**Key Validation:**
```python
# Format validation catches common issues
is_valid = handler.api_key_validator.validate_key_format(
    key,
    'huggingface'  # Format-specific validation
)

# Connection testing verifies key works
can_connect = handler.api_key_validator.test_api_connection(
    'https://api.huggingface.co/models',
    {'Authorization': f'Bearer {key}'}
)
```

### Access Control

**Component-Level Security:**
- Implement role-based access control (RBAC)
- Restrict admin operations
- Log all access attempts
- Monitor for unauthorized access

**Integration-Level Security:**
- Limit API scopes to minimum required
- Use separate keys for different integrations
- Implement rate limiting per integration
- Monitor for unusual access patterns

### Audit Trail

**Maintain Complete Audit Log:**
- All authentication attempts
- All configuration changes
- All API calls (with sanitized data)
- All error conditions
- All security events

---

## API Integration Patterns

### Request/Response Pattern

**Standard Integration Flow:**
```python
# 1. Validate inputs
if not validate_input(request_data):
    return ErrorContext('api', 'validation', request=request_data)

# 2. Check rate limits
if is_rate_limited(api_name):
    return handle_integration_error(
        api_name,
        IntegrationErrorType.RATE_LIMIT_EXCEEDED,
        None,
        context
    )

# 3. Prepare request with timeout
request = prepare_request(
    url=api_endpoint,
    headers=get_auth_headers(api_key),
    timeout=30
)

# 4. Execute with error handling
try:
    response = execute_request(request)
    return response.json()
except Exception as e:
    return handle_integration_error(
        api_name,
        classify_error_type(e),
        e,
        context
    )
```

### Retry Strategy

**Exponential Backoff Implementation:**
```python
def retry_with_backoff(func, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt < max_attempts - 1:
                wait_time = 2 ** attempt  # 1, 2, 4 seconds
                time.sleep(wait_time)
            else:
                raise
```

**Retry Conditions:**
- Retry on: Connection timeout, rate limit, service unavailable
- Don't retry on: Invalid API key, authentication failed, bad request
- Max retries: 3 (configurable)
- Max wait time: 60 seconds

### Fallback Pattern

**Implementing Fallbacks:**
```python
# Try primary API
try:
    result = call_primary_api(request)
    return result
except Exception as e:
    handler.handle_integration_error(
        'primary_api',
        error_type,
        e,
        context
    )
    
    # Fall back to secondary API
    try:
        result = call_fallback_api(request)
        return result
    except Exception as e2:
        handler.handle_integration_error(
            'fallback_api',
            error_type,
            e2,
            context
        )
        raise
```

---

## Database Operations

### Query Performance Best Practices

**Indexes:**
- Index frequently queried columns
- Use composite indexes for multi-column queries
- Avoid over-indexing (impacts write performance)
- Monitor index usage and remove unused indexes

**Query Optimization:**
- Use EXPLAIN ANALYZE to understand query plans
- Avoid SELECT * - specify needed columns
- Use proper JOINs instead of filtering in code
- Use LIMIT to reduce result sets
- Use WHERE clauses to filter early

### Connection Management

**Connection Pooling:**
- Set pool size to 5-20 (based on workload)
- Set connection timeout to 5-30 seconds
- Monitor pool utilization
- Implement pool exhaustion detection

**Connection Lifecycle:**
```python
# Create connection from pool
connection = pool.get_connection()

try:
    # Use connection
    result = connection.execute(query)
    return result
finally:
    # Always return connection to pool
    pool.return_connection(connection)
```

### Transaction Management

**ACID Compliance:**
- Use transactions for multi-step operations
- Implement proper rollback on error
- Use connection isolation levels appropriately
- Monitor transaction duration

**Best Practices:**
- Keep transactions short
- Avoid user interaction within transactions
- Use read-only transactions where possible
- Implement deadlock detection and retry

---

## Checklist for Operations

### Daily Operations
- [ ] Review error logs for new issues
- [ ] Monitor system health metrics
- [ ] Check API integration status
- [ ] Verify backup completion
- [ ] Review performance metrics

### Weekly Operations
- [ ] Analyze error trends
- [ ] Review performance reports
- [ ] Check API key expiration dates
- [ ] Test disaster recovery procedures
- [ ] Security audit of access logs

### Monthly Operations
- [ ] Performance optimization review
- [ ] Capacity planning analysis
- [ ] Security assessment
- [ ] Dependency updates
- [ ] Configuration review

### Quarterly Operations
- [ ] API key rotation
- [ ] Major version updates
- [ ] Complete system audit
- [ ] Disaster recovery drill
- [ ] Vendor assessment

---

## Additional Resources

- [Error Handler Documentation](gatekeeper_error_handler.py)
- [Integration Setup Guide](SETUP_DEVELOPER_INTEGRATIONS.py)
- [Database Guides](DATABASE_GUIDES_COMPLETE.md)
- [Educational System](EDUCATIONAL_SYSTEM_COMPLETE.md)
- [Performance Optimization](UI_PANEL_OPTIMIZATION_RESUME_GUIDE.md)

**System Status:** All operational systems documented and ready for production deployment.
