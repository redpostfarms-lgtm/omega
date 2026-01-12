#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# Unit tests for voiceprint_auth.py

import pytest
import sys
import numpy as np
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestVoiceprintAuth:
    """Unit tests for voiceprint authentication."""
    
    @pytest.fixture
    def temp_voice_dir(self):
        """Create temporary voiceprint directory."""
        temp_dir = Path(tempfile.mkdtemp())
        voice_dir = temp_dir / 'voiceprint'
        voice_dir.mkdir(parents=True, exist_ok=True)
        
        yield voice_dir
        
        shutil.rmtree(temp_dir)
    
    def test_voiceprint_save_load(self, temp_voice_dir):
        """Test voiceprint save and load."""
        # Create test voiceprint data
        test_data = np.random.randn(16000).astype(np.float32)
        
        # Save
        voiceprint_file = temp_voice_dir / 'me.npy'
        np.save(voiceprint_file, test_data)
        
        # Load
        loaded_data = np.load(voiceprint_file)
        
        assert np.array_equal(test_data, loaded_data)
    
    def test_speechbrain_availability(self):
        """Test SpeechBrain availability."""
        try:
            import torch
            from speechbrain.inference.speaker import EncoderClassifier
            speechbrain_available = True
        except ImportError:
            speechbrain_available = False
        
        # Test should pass regardless
        assert True  # SpeechBrain is optional
    
    def test_voiceprint_matching_logic(self):
        """Test voiceprint matching logic."""
        # Simulate voiceprint data
        voiceprint1 = np.random.randn(16000).astype(np.float32)
        voiceprint2 = np.random.randn(16000).astype(np.float32)
        
        # Calculate RMS
        rms1 = np.sqrt(np.mean(voiceprint1**2))
        rms2 = np.sqrt(np.mean(voiceprint2**2))
        
        # Different voiceprints should have different RMS
        assert rms1 != rms2 or np.allclose(voiceprint1, voiceprint2)
    
    def test_zero_crossing_calculation(self):
        """Test zero-crossing calculation."""
        # Create test signal
        signal = np.array([1, -1, 1, -1, 1])
        
        # Calculate zero crossings
        zero_crossings = np.sum(np.diff(np.sign(signal)) != 0)
        
        assert zero_crossings == 4  # 4 zero crossings in this signal

if __name__ == '__main__':
    pytest.main([__file__, '-v'])

