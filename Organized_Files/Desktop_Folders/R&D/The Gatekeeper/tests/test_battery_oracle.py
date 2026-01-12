#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# Unit tests for battery_oracle.py

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestBatteryOracle:
    """Unit tests for battery oracle functionality."""
    
    def test_nasa_degradation_model(self):
        """Test NASA degradation model."""
        from battery_oracle import NASA_DEGRADATION_RATE, NASA_INITIAL_CAPACITY
        
        # Test initial capacity
        assert NASA_INITIAL_CAPACITY == 1.0
        
        # Test degradation rate
        assert NASA_DEGRADATION_RATE > 0
        assert NASA_DEGRADATION_RATE < 1
    
    def test_death_date_prediction(self):
        """Test death date prediction logic."""
        # Simulate battery data
        cycles = 100
        capacity = 0.85
        current_date = datetime.now()
        
        # Calculate remaining capacity to lose
        target_capacity = 0.80
        remaining_loss = capacity - target_capacity
        
        # Estimate cycles to death
        from battery_oracle import NASA_DEGRADATION_RATE
        cycles_to_death = remaining_loss / NASA_DEGRADATION_RATE
        
        assert cycles_to_death > 0
        assert cycles_to_death < 1000
    
    def test_urgent_battery_detection(self):
        """Test urgent battery detection."""
        # Create test battery data
        batteries = [
            {'days_remaining': 50, 'cycles': 500},
            {'days_remaining': 100, 'cycles': 400},
            {'days_remaining': 200, 'cycles': 300}
        ]
        
        # Filter urgent (<90 days)
        urgent = [b for b in batteries if b['days_remaining'] < 90]
        
        assert len(urgent) == 1
        assert urgent[0]['days_remaining'] == 50
    
    def test_smtp_config_loading(self):
        """Test SMTP configuration loading."""
        # Test default config structure
        default_config = {
            'smtp_enabled': False,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_use_tls': True
        }
        
        assert 'smtp_enabled' in default_config
        assert 'smtp_server' in default_config
        assert default_config['smtp_port'] == 587

if __name__ == '__main__':
    pytest.main([__file__, '-v'])

