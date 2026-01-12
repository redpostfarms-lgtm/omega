#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# FARMHUB SELF-DIAGNOSE
# Diagnoses and heals sensor connectivity issues

import sys
import io
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
FARMHUB = BRAIN / 'FarmHub'

def diagnose_sensors():
    """Diagnose sensor connectivity."""
    print("[INFO] Running sensor diagnostics...")
    
    # Check MQTT broker
    try:
        import paho.mqtt.client as mqtt
        client = mqtt.Client()
        client.connect('localhost', 1883, 5)
        print("[OK] MQTT broker: Connected")
        client.disconnect()
    except Exception as e:
        print(f"[ERROR] MQTT broker: {e}")
    
    # Check Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("[OK] Redis: Connected")
    except Exception as e:
        print(f"[WARNING] Redis: {e}")
    
    # Check sensor log
    log_file = FARMHUB / 'sensor_log.csv'
    if log_file.exists():
        print(f"[OK] Sensor log: {log_file} exists")
    else:
        print(f"[WARNING] Sensor log: {log_file} not found")
    
    print("[OK] Self-diagnose complete")

if __name__ == "__main__":
    diagnose_sensors()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

