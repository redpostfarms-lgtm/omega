#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# Pytest configuration and shared fixtures

import pytest
import sys
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope='session')
def test_data_dir():
    """Create test data directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_brain_path(monkeypatch):
    """Mock D:\RPF_BRAIN path for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    brain_path = temp_dir / 'RPF_BRAIN'
    brain_path.mkdir(parents=True, exist_ok=True)
    
    # Mock the path
    import brain_prime
    monkeypatch.setattr(brain_prime, 'ROOT', brain_path / 'Archived')
    
    yield brain_path
    
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_voiceprint_dir(monkeypatch):
    """Mock voiceprint directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    voice_dir = temp_dir / 'voiceprint'
    voice_dir.mkdir(parents=True, exist_ok=True)
    
    yield voice_dir
    
    shutil.rmtree(temp_dir)

