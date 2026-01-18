#!/usr/bin/env python3
"""
Test TTS Monitoring Integration
================================
Quick test to verify TTS monitoring is working correctly.
"""

import asyncio
import time
from pathlib import Path
from omega_monitoring import get_monitor
from omega_optimized_tts import initialize_tts_preload, tts_to_file_optimized

def test_monitoring_integration():
    """Test that TTS monitoring is integrated and working."""
    print("=" * 70)
    print("  TTS MONITORING INTEGRATION TEST")
    print("=" * 70)
    print()

    # Get monitor instance
    monitor = get_monitor()
    print("[1/5] Monitor initialized")

    # Initialize TTS
    print("[2/5] Initializing TTS model...")
    initialize_tts_preload()
    print("      ✓ TTS model ready")

    # Get baseline metrics
    baseline_metrics = monitor.get_metrics()
    baseline_tts_count = baseline_metrics['counters'].get('tts_generation_total', 0)
    print(f"[3/5] Baseline TTS generations: {baseline_tts_count}")

    # Generate test audio
    print("[4/5] Generating test audio...")
    test_text = "Hello, this is a test of the TTS monitoring system."

    try:
        output_file = tts_to_file_optimized(test_text, output_file='test_monitoring.wav')
        print(f"      ✓ Audio generated: {output_file}")
    except Exception as e:
        print(f"      ✗ Error: {e}")
        return False

    # Check metrics
    print("[5/5] Checking metrics...")
    time.sleep(0.1)  # Small delay to ensure metrics are recorded

    updated_metrics = monitor.get_metrics()
    new_tts_count = updated_metrics['counters'].get('tts_generation_total', 0)
    tts_errors = updated_metrics['counters'].get('tts_generation_errors', 0)

    print()
    print("=" * 70)
    print("  RESULTS")
    print("=" * 70)
    print(f"  TTS Generations: {baseline_tts_count} → {new_tts_count}")
    print(f"  TTS Errors: {tts_errors}")

    # Check if we have duration metrics
    if 'tts_generation_duration' in updated_metrics['histograms']:
        duration_data = updated_metrics['histograms']['tts_generation_duration']
        if duration_data['count'] > 0:
            print(f"  Average Duration: {duration_data['mean']:.3f}s")
            print(f"  Min Duration: {duration_data['min']:.3f}s")
            print(f"  Max Duration: {duration_data['max']:.3f}s")

    print("=" * 70)
    print()

    # Verify monitoring worked
    if new_tts_count > baseline_tts_count:
        print("✓ SUCCESS: TTS monitoring is working!")
        print(f"  Counter incremented: {baseline_tts_count} → {new_tts_count}")

        # Save metrics report
        monitor.save_metrics()
        print(f"  Metrics saved to: metrics.json")

        return True
    else:
        print("✗ FAILURE: TTS monitoring did not record the generation")
        print("  Check that omega_monitoring imports are correct")
        return False

if __name__ == "__main__":
    success = test_monitoring_integration()
    exit(0 if success else 1)
