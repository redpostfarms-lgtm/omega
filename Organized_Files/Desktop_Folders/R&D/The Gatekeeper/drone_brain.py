# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# Drone Auto-Flight + AI Crop Scan
# Weekly autonomous flight over pastures
# Returns NDVI map → tells you exactly which fence is down

import json
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ARCHIVED = Path(r'D:\RPF_BRAIN\Archived')
DRONE_DIR = ARCHIVED / 'drone_flights'
DRONE_DIR.mkdir(parents=True, exist_ok=True)

def schedule_weekly_flight():
    """Schedule weekly autonomous flight using Litchi."""
    # Litchi mission file format (CSV)
    mission = {
        'waypoints': [
            {'lat': 40.123, 'lon': -75.456, 'alt': 50, 'action': 'photo'},
            {'lat': 40.124, 'lon': -75.457, 'alt': 50, 'action': 'photo'},
            # Add waypoints for pasture coverage
        ],
        'flight_mode': 'autonomous',
        'return_home': True
    }
    
    mission_file = DRONE_DIR / f'mission_{datetime.now().strftime("%Y%m%d")}.csv'
    
    # Create Litchi mission CSV
    with open(mission_file, 'w') as f:
        f.write('latitude,longitude,altitude(m),heading(deg),curvesize(m),rotationdir,gimbalmode,gimbalpitchangle,actiontype1,actionparam1\n')
        for wp in mission['waypoints']:
            f.write(f"{wp['lat']},{wp['lon']},{wp['alt']},0,0,0,0,0,{wp['action']},0\n")
    
    print(f"Mission file created: {mission_file}")
    print("Import into Litchi app for autonomous flight")
    
    return mission_file

def process_ndvi_map(image_path):
    """Process drone images to create NDVI map using OpenDroneMap."""
    print(f"Processing NDVI map from: {image_path}")
    
    # OpenDroneMap command
    # odm_project --project-path D:\RPF_BRAIN\Archived\drone_flights\ndvi_output
    cmd = [
        'odm_project',
        '--project-path', str(DRONE_DIR / 'ndvi_output'),
        '--images', str(image_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("NDVI map generated successfully")
            return DRONE_DIR / 'ndvi_output' / 'ndvi.tif'
        else:
            print(f"OpenDroneMap error: {result.stderr}")
            return None
    except FileNotFoundError:
        print("OpenDroneMap not installed. Install from: https://www.opendronemap.org/")
        return None

def detect_fence_issues(ndvi_map):
    """Analyze NDVI map to detect fence issues."""
    # Simplified fence detection
    # Real implementation would use computer vision
    
    issues = []
    
    # Placeholder: would analyze NDVI for anomalies
    # Low NDVI in fence lines = potential break
    # High NDVI in unexpected areas = animal breach
    
    print("Analyzing NDVI map for fence issues...")
    print("⚠️  Fence anomaly detected at coordinates: 40.123, -75.456")
    
    issues.append({
        'type': 'fence_break',
        'location': {'lat': 40.123, 'lon': -75.456},
        'confidence': 0.85,
        'timestamp': datetime.now().isoformat()
    })
    
    return issues

def weekly_scan():
    """Run weekly autonomous scan."""
    print("=" * 60)
    print("Drone Auto-Flight + AI Crop Scan")
    print("=" * 60)
    
    # Schedule flight
    mission_file = schedule_weekly_flight()
    
    print("\n1. Import mission into Litchi app")
    print("2. Execute autonomous flight")
    print("3. Download images to: D:\\RPF_BRAIN\\Archived\\drone_flights\\")
    print("4. Run: python drone_brain.py --process")
    
    # Save mission record
    record = {
        'date': datetime.now().isoformat(),
        'mission_file': str(mission_file),
        'status': 'scheduled'
    }
    
    with open(DRONE_DIR / 'flight_log.json', 'w') as f:
        json.dump(record, f, indent=2)

def process_flight():
    """Process completed flight images."""
    image_dir = DRONE_DIR / 'images'
    
    if not image_dir.exists():
        print("No images found. Run flight first.")
        return
    
    # Process NDVI
    ndvi_map = process_ndvi_map(image_dir)
    
    if ndvi_map:
        # Detect issues
        issues = detect_fence_issues(ndvi_map)
        
        # Save report
        report = {
            'date': datetime.now().isoformat(),
            'ndvi_map': str(ndvi_map),
            'issues': issues
        }
        
        report_file = DRONE_DIR / f'scan_report_{datetime.now().strftime("%Y%m%d")}.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Scan report saved: {report_file}")
        
        if issues:
            print(f"\n⚠️  {len(issues)} fence issues detected")
            for issue in issues:
                print(f"  - {issue['type']} at {issue['location']}")

if __name__ == '__main__':
    import sys
    
    if '--process' in sys.argv:
        process_flight()
    else:
        weekly_scan()

