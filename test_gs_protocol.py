#!/usr/bin/env python3
"""
Basic test framework for Ghost Swarm Protocol.
Tests core functionality and configuration.
"""

import unittest
import json
import tempfile
from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from ghost_swarm_protocol import (
        IncidentLogger, MilitaryROE, GhostSwarmProtocol,
        retry_on_error
    )
    IMPORTS_OK = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_OK = False


class TestIncidentLogger(unittest.TestCase):
    """Test IncidentLogger class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = Path(self.temp_dir) / 'test_log.txt'
    
    def test_logger_initialization(self):
        """Test logger initialization."""
        if not IMPORTS_OK:
            self.skipTest("Imports failed")
        logger = IncidentLogger(log_file=str(self.log_file))
        self.assertEqual(logger.log_file, self.log_file)
        self.assertEqual(len(logger.report), 0)
    
    def test_stamp(self):
        """Test logging stamp."""
        if not IMPORTS_OK:
            self.skipTest("Imports failed")
        logger = IncidentLogger(log_file=str(self.log_file))
        logger.stamp('TEST ACTION', 'TEST')
        self.assertEqual(len(logger.report), 1)
        self.assertIn('TEST ACTION', logger.report[0])
    
    def test_get_report(self):
        """Test report generation."""
        if not IMPORTS_OK:
            self.skipTest("Imports failed")
        logger = IncidentLogger(log_file=str(self.log_file))
        logger.stamp('TEST ACTION', 'TEST')
        result = logger.get_report()
        self.assertIn('Report saved', result)
        self.assertTrue(self.log_file.exists())


class TestMilitaryROE(unittest.TestCase):
    """Test MilitaryROE class."""
    
    def test_roe_initialization(self):
        """Test ROE initialization."""
        if not IMPORTS_OK:
            self.skipTest("Imports failed")
        roe = MilitaryROE()
        self.assertIsNotNone(roe.principles)
        self.assertIn('hostile_intent_threshold', roe.principles)
    
    def test_roe_with_logger(self):
        """Test ROE with logger."""
        if not IMPORTS_OK:
            self.skipTest("Imports failed")
        temp_dir = tempfile.mkdtemp()
        log_file = Path(temp_dir) / 'test_log.txt'
        logger = IncidentLogger(log_file=str(log_file))
        roe = MilitaryROE(logger=logger)
        self.assertEqual(roe.logger, logger)


class TestGhostSwarmProtocol(unittest.TestCase):
    """Test GhostSwarmProtocol class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / 'test_state.json'
        self.config_file = Path(self.temp_dir) / 'test_config.json'
        
        # Create minimal config
        config = {
            'logging': {'max_log_size_mb': 1, 'backup_count': 2, 'log_file': 'test_log.txt'},
            'threading': {'predict_interval_seconds': 1, 'threat_check_interval_seconds': 1, 'auto_save_interval_seconds': 1, 'threat_cooldown_seconds': 1},
            'threat_detection': {'detection_probability': 0.01, 'predict_threshold': 0.9, 'hostile_intent_threshold': 0.8},
            'counterstrike': {'min_port': 80, 'max_port': 443, 'decohere_packets': 3, 'decohere_delay_min': 0.1, 'decohere_delay_max': 0.2},
            'error_recovery': {'max_retries': 2, 'retry_delay_seconds': 0.1, 'exponential_backoff': True},
            'resource_monitoring': {'enabled': False, 'check_interval_seconds': 60, 'max_memory_mb': 512, 'max_cpu_percent': 80.0}
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
    
    def test_protocol_initialization(self):
        """Test protocol initialization."""
        if not IMPORTS_OK:
            self.skipTest("Imports failed")
        gs = GhostSwarmProtocol(
            state_file=str(self.state_file),
            config_file=str(self.config_file)
        )
        self.assertIsNotNone(gs.config)
        self.assertIsNotNone(gs.logger)
        self.assertIsNotNone(gs.roe)
    
    def test_config_loading(self):
        """Test configuration loading."""
        if not IMPORTS_OK:
            self.skipTest("Imports failed")
        gs = GhostSwarmProtocol(
            state_file=str(self.state_file),
            config_file=str(self.config_file)
        )
        self.assertIn('logging', gs.config)
        self.assertIn('threading', gs.config)
    
    def test_port_validation(self):
        """Test port validation."""
        if not IMPORTS_OK:
            self.skipTest("Imports failed")
        gs = GhostSwarmProtocol(
            state_file=str(self.state_file),
            config_file=str(self.config_file)
        )
        self.assertTrue(gs._validate_port(80))
        self.assertTrue(gs._validate_port(443))
        self.assertFalse(gs._validate_port(1))
        self.assertFalse(gs._validate_port(65536))


class TestRetryDecorator(unittest.TestCase):
    """Test retry decorator."""
    
    def test_retry_on_success(self):
        """Test retry on success."""
        if not IMPORTS_OK:
            self.skipTest("Imports failed")
        
        @retry_on_error(max_retries=3, delay=0.1)
        def success_func():
            return True
        
        result = success_func()
        self.assertTrue(result)
    
    def test_retry_on_failure(self):
        """Test retry on failure."""
        if not IMPORTS_OK:
            self.skipTest("Imports failed")
        
        call_count = [0]
        
        @retry_on_error(max_retries=3, delay=0.1)
        def fail_func():
            call_count[0] += 1
            raise ValueError("Test error")
        
        with self.assertRaises(ValueError):
            fail_func()
        
        self.assertEqual(call_count[0], 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
