#!/usr/bin/env python3
"""
Monitor voice analysis execution status
"""
import os
import time
import json
from pathlib import Path
from datetime import datetime

def check_status():
    status = {
        "timestamp": datetime.now().isoformat(),
        "voice_files": {},
        "output_files": {},
        "logs": {}
    }
    
    # Check voice input files
    for voice_file in ['clip_0001.wav', 'omega_downloaded.wav']:
        if os.path.exists(voice_file):
            stat = os.stat(voice_file)
            status["voice_files"][voice_file] = {
                "size_mb": round(stat.st_size / (1024*1024), 2),
                "exists": True
            }
    
    # Check output files
    for pattern in ['omega_voice_*.wav']:
        import glob
        files = glob.glob(pattern)
        for f in files:
            stat = os.stat(f)
            status["output_files"][f] = {
                "size_mb": round(stat.st_size / (1024*1024), 2)
            }
    
    # Check logs
    import glob
    for log_file in glob.glob('voice_output_*.log'):
        stat = os.stat(log_file)
        status["logs"][log_file] = {
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    
    return status

if __name__ == "__main__":
    status = check_status()
    print(json.dumps(status, indent=2))
    
    # Print summary
    print("\n" + "="*70)
    print("VOICE ANALYSIS STATUS CHECK")
    print("="*70)
    
    print("\nInput Files:")
    for name, info in status["voice_files"].items():
        print(f"  ✓ {name}: {info['size_mb']} MB")
    
    if status["output_files"]:
        print("\nGenerated Output Files:")
        for name, info in status["output_files"].items():
            print(f"  ✓ {name}: {info['size_mb']} MB")
    else:
        print("\nGenerated Output Files:")
        print("  ⏳ Waiting for voice cloning generation...")
    
    print("\nProcess Logs:")
    for log, info in status["logs"].items():
        size_kb = round(info['size_bytes'] / 1024, 1)
        print(f"  📝 {log}: {size_kb} KB (Modified: {info['modified']})")
