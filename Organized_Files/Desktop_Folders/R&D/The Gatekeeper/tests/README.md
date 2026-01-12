# The Gatekeeper Test Suite

**Red Post Farms, LLC | Copyright (c) 2025-2026 | All Rights Reserved**

## Overview

Comprehensive test suite for The Gatekeeper system using pytest.

## Installation

```bash
pip install pytest pytest-cov
```

## Running Tests

### Run all tests:
```bash
pytest tests/
```

### Run with coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run specific test file:
```bash
pytest tests/test_brain_prime.py
```

### Run with verbose output:
```bash
pytest tests/ -v
```

## Test Structure

- `test_brain_prime.py` - Knowledge upload system tests
- `test_auto_heal.py` - Self-healing system tests
- `test_voiceprint_auth.py` - Voice authentication tests
- `test_battery_oracle.py` - Battery monitoring tests
- `test_integration.py` - End-to-end integration tests
- `conftest.py` - Shared fixtures and configuration

## Test Coverage

**Target:** 80%+ coverage for core modules

**Current Coverage:**
- Unit Tests: Core functionality
- Integration Tests: Workflow verification
- Mock Tests: External dependencies

## Notes

- Tests use temporary directories to avoid modifying production data
- External dependencies (APIs, hardware) are mocked
- Tests are designed to run offline

