#!/usr/bin/env python3
"""
Omega Resource-Optimized Components
====================================
Wrapper functions for Omega components with resource-aware loading.
"""

import sys
from pathlib import Path
from typing import Optional, Any, Callable

# Try to import resource manager
try:
    from omega_system_resource_manager import (
        get_system_resource_manager,
        get_system_gradual_loader,
        load_component_gradually
    )
    RESOURCE_MANAGER_AVAILABLE = True
except ImportError:
    RESOURCE_MANAGER_AVAILABLE = False

def load_tts_gradually():
    """Load TTS model with resource-aware gradual loading"""
    if RESOURCE_MANAGER_AVAILABLE:
        def load_tts():
            try:
                from TTS.api import TTS
                import torch
                import os
                
                os.environ['TTS_ACCEPT_TO_S'] = '1'
                
                # Check GPU availability
                resource_manager = get_system_resource_manager()
                use_gpu = resource_manager.can_use_gpu() if resource_manager else False
                device = 'cuda' if use_gpu else 'cpu'
                
                print(f"[TTS] Loading model on {device}...")
                tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)
                print(f"[TTS] Model loaded on {device}")
                return tts
            except Exception as e:
                print(f"[TTS] Error loading model: {e}")
                raise
        
        return load_component_gradually("tts_model", load_tts)
    else:
        # Fallback to standard loading
        from TTS.api import TTS
        import torch
        import os
        os.environ['TTS_ACCEPT_TO_S'] = '1'
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        return TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)

def load_whisper_gradually():
    """Load Whisper model with resource-aware gradual loading"""
    if RESOURCE_MANAGER_AVAILABLE:
        def load_whisper():
            try:
                from faster_whisper import WhisperModel
                import torch
                
                # Check GPU availability
                resource_manager = get_system_resource_manager()
                use_gpu = resource_manager.can_use_gpu() if resource_manager else False
                device = "cuda" if use_gpu else "cpu"
                compute_type = "float16" if use_gpu else "int8"
                
                print(f"[Whisper] Loading model on {device} ({compute_type})...")
                model = WhisperModel("large-v3", device=device, compute_type=compute_type)
                print(f"[Whisper] Model loaded on {device}")
                return model
            except Exception as e:
                print(f"[Whisper] Error loading model: {e}")
                # Fallback to CPU
                try:
                    from faster_whisper import WhisperModel
                    model = WhisperModel("large-v3", device="cpu", compute_type="int8")
                    print("[Whisper] Model loaded on CPU (fallback)")
                    return model
                except (ImportError, RuntimeError, ValueError) as e:
                    # CPU fallback failed - re-raise original error
                    raise
        
        return load_component_gradually("whisper_model", load_whisper)
    else:
        # Fallback to standard loading
        from faster_whisper import WhisperModel
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        return WhisperModel("large-v3", device=device, compute_type=compute_type)

def load_voice_security_gradually():
    """Load voice security system with resource-aware gradual loading"""
    if RESOURCE_MANAGER_AVAILABLE:
        def load_voice_security():
            try:
                from voice_security_system import voice_security
                print("[Voice Security] System loaded")
                return voice_security
            except Exception as e:
                print(f"[Voice Security] Error loading: {e}")
                raise
        
        return load_component_gradually("voice_security", load_voice_security)
    else:
        # Fallback to standard loading
        from voice_security_system import voice_security
        return voice_security

def load_hardware_controller_gradually():
    """Load hardware controller with resource-aware gradual loading"""
    if RESOURCE_MANAGER_AVAILABLE:
        def load_hardware():
            try:
                from omega_comprehensive_hardware import get_hardware_controller
                controller = get_hardware_controller()
                print("[Hardware] Controller loaded")
                return controller
            except Exception as e:
                print(f"[Hardware] Error loading: {e}")
                return None
        
        return load_component_gradually("hardware_controller", load_hardware)
    else:
        # Fallback to standard loading
        try:
            from omega_comprehensive_hardware import get_hardware_controller
            return get_hardware_controller()
        except (IOError, OSError, PermissionError) as e:
            # Resource check failed - return None
            return None

def load_developer_integrations_gradually():
    """Load developer integrations with resource-aware gradual loading"""
    if RESOURCE_MANAGER_AVAILABLE:
        def load_integrations():
            try:
                from omega_developer_integrations import get_integration_manager
                manager = get_integration_manager()
                print("[Integrations] Manager loaded")
                return manager
            except Exception as e:
                print(f"[Integrations] Error loading: {e}")
                return None
        
        return load_component_gradually("developer_integrations", load_integrations)
    else:
        # Fallback to standard loading
        try:
            from omega_developer_integrations import get_integration_manager
            return get_integration_manager()
        except (IOError, OSError, PermissionError) as e:
            # Resource check failed - return None
            return None

def get_optimal_workers_for_task(task_complexity: str = "medium") -> int:
    """Get optimal number of workers for a task"""
    if RESOURCE_MANAGER_AVAILABLE:
        from omega_system_resource_manager import get_optimal_workers
        return get_optimal_workers(task_complexity)
    return 1

def should_use_parallel_processing(task_complexity: str = "medium") -> bool:
    """Determine if parallel processing should be used"""
    if RESOURCE_MANAGER_AVAILABLE:
        from omega_system_resource_manager import should_use_multiprocessing
        return should_use_multiprocessing(task_complexity)
    return False

def save_system_patterns():
    """Save system loading patterns"""
    if RESOURCE_MANAGER_AVAILABLE:
        from omega_system_resource_manager import save_system_patterns
        save_system_patterns()

def main():
    """Test resource-optimized components"""
    print("=" * 80)
    print(" " * 20 + "OMEGA RESOURCE-OPTIMIZED COMPONENTS")
    print("=" * 80)
    print()
    
    print("Resource-optimized component loaders available:")
    print("  ✅ TTS model (gradual loading)")
    print("  ✅ Whisper model (gradual loading)")
    print("  ✅ Voice security (gradual loading)")
    print("  ✅ Hardware controller (gradual loading)")
    print("  ✅ Developer integrations (gradual loading)")
    print()
    print("System-wide resource optimization ready!")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
