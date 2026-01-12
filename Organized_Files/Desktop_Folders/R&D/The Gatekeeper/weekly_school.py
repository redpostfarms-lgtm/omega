#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# WEEKLY_SCHOOL.PY - Auto-update knowledge base weekly
# Keeps all knowledge bases current with latest data
# Date: 2026-01-03 17:41 MST

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROOT = Path(r'D:\RPF_BRAIN')
KB_ROOT = ROOT / 'KB'
STATE_FILE = ROOT / 'The Gatekeeper' / 'school_state.json'
LOG_FILE = ROOT / 'The Gatekeeper' / 'school_log.txt'

# Create directories
KB_ROOT.mkdir(parents=True, exist_ok=True)
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_state():
    """Load last update state."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        'last_update': None,
        'update_frequency_days': 7,
        'sources': {}
    }

def save_state(state):
    """Save update state."""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def log(message):
    """Log message to file and console."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {message}\n"
    print(log_msg.strip())
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg)

def check_wget():
    """Check if wget is available."""
    try:
        result = subprocess.run(['wget', '--version'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def update_source(source_name, url, target_dir, options=""):
    """Update a single knowledge source."""
    log(f"Updating {source_name}...")
    
    target_path = KB_ROOT / target_dir
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Build wget command
    cmd = ['wget']
    
    # Add options
    if 'mirror' in options:
        cmd.extend(['--mirror', '--no-parent', '--no-host-directories'])
    else:
        cmd.append('--continue')
    
    cmd.extend(['--tries=3', '--timeout=300', '--limit-rate=10M'])
    
    if 'mirror' in options:
        cmd.extend(['--cut-dirs=2'])
        if 'accept' in options:
            cmd.extend(['--accept', '*.csv,*.json,*.jsonl,*.gz,*.zip,*.pdf,*.html,*.xml,*.tif,*.vrt,*.sdf,*.xlsx'])
        cmd.append(url)
        cmd.extend(['-P', str(target_path)])
    else:
        cmd.append(url)
        cmd.extend(['-O', str(target_path / f"{source_name.lower().replace(' ', '_')}.dat")])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        if result.returncode == 0:
            log(f"  [OK] {source_name} updated successfully")
            return True
        else:
            log(f"  [WARNING] {source_name} update failed: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        log(f"  [WARNING] {source_name} update timed out")
        return False
    except Exception as e:
        log(f"  [ERROR] {source_name} update error: {e}")
        return False

def should_update(state, source_name):
    """Check if source should be updated."""
    if source_name not in state['sources']:
        return True
    
    last_update_str = state['sources'][source_name].get('last_update')
    if not last_update_str:
        return True
    
    try:
        last_update = datetime.fromisoformat(last_update_str)
        days_since = (datetime.now() - last_update).days
        return days_since >= state['update_frequency_days']
    except:
        return True

def main():
    """Main update loop."""
    log("=" * 60)
    log("GATEKEEPER WEEKLY SCHOOL - Auto-Update Knowledge Base")
    log("=" * 60)
    
    # Check wget
    if not check_wget():
        log("ERROR: wget not found. Please install wget for Windows.")
        log("Download from: https://eternallybored.org/misc/wget/")
        return 1
    
    # Load state
    state = load_state()
    
    # Knowledge sources to update
    sources = [
        {
            'name': 'iNaturalist GBIF',
            'url': 'https://download.inaturalist.org/observations/gbif-2026-partial/',
            'target': 'Botany/iNaturalist',
            'options': 'mirror accept'
        },
        {
            'name': 'Plant.id',
            'url': 'https://files.plant.id/open-dataset/2026-dump.tar.gz',
            'target': 'Botany',
            'options': 'continue'
        },
        {
            'name': 'USDA Web Soil Survey',
            'url': 'https://websoilsurvey.sc.egov.usda.gov/DSD/Download/',
            'target': 'Earth/USDA',
            'options': 'mirror accept'
        },
        {
            'name': 'ISRIC SoilGrids',
            'url': 'https://files.isric.org/soilgrids/latest/data/',
            'target': 'Earth/SoilGrids',
            'options': 'mirror accept'
        },
        {
            'name': 'ChEMBL',
            'url': 'https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/chembl_33_sqlite.tar.gz',
            'target': 'Chem/ChEMBL',
            'options': 'continue'
        },
        {
            'name': 'IVIS Open Books',
            'url': 'https://www.ivis.org/openbooks/',
            'target': 'Vet/IVIS',
            'options': 'mirror accept'
        },
        {
            'name': 'USDA FoodData Central',
            'url': 'https://fdc.nal.usda.gov/fdc-app.html#/download',
            'target': 'Nutrition/USDA_FDC',
            'options': 'mirror accept'
        },
        {
            'name': 'Feedipedia',
            'url': 'https://www.feedipedia.org/node/7358',
            'target': 'Nutrition',
            'options': 'continue'
        }
    ]
    
    # Update sources that need updating
    updated_count = 0
    skipped_count = 0
    failed_count = 0
    
    for source in sources:
        if should_update(state, source['name']):
            success = update_source(
                source['name'],
                source['url'],
                source['target'],
                source['options']
            )
            
            # Update state
            if source['name'] not in state['sources']:
                state['sources'][source['name']] = {}
            
            state['sources'][source['name']]['last_update'] = datetime.now().isoformat()
            state['sources'][source['name']]['success'] = success
            
            if success:
                updated_count += 1
            else:
                failed_count += 1
        else:
            log(f"Skipping {source['name']} (updated recently)")
            skipped_count += 1
    
    # Update global last update time
    state['last_update'] = datetime.now().isoformat()
    save_state(state)
    
    # Summary
    log("=" * 60)
    log(f"Update complete: {updated_count} updated, {skipped_count} skipped, {failed_count} failed")
    log(f"Next update in {state['update_frequency_days']} days")
    log("=" * 60)
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("Update interrupted by user")
        sys.exit(1)
    except Exception as e:
        log(f"Fatal error: {e}")
        sys.exit(1)

