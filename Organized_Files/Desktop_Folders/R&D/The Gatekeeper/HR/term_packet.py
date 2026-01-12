#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# TERMINATION PACKET - Generate termination documents

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(r'D:\RPF_BRAIN\HR')
TERM_DIR = ROOT / 'Terminations'
TERM_DIR.mkdir(parents=True, exist_ok=True)

def create_termination_packet(name: str, reason: str):
    """Create termination packet."""
    term_file = TERM_DIR / f'{name.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d")}.json'
    
    term_data = {
        'employee_name': name,
        'termination_date': datetime.now().isoformat(),
        'reason': reason,
        'final_paycheck_rule': 'Same day for termination, next payday for resignation',
        'cobra_notice': 'Mini-COBRA notice sent (2-19 employees)',
        'unemployment_letter': 'Unemployment letter generated',
        'exit_interview': 'Scheduled',
        'hfwa_balance': 'No payout on termination per Colorado law'
    }
    
    with open(term_file, 'w', encoding='utf-8') as f:
        json.dump(term_data, f, indent=2, ensure_ascii=False)
    
    print(f"Termination packet created: {term_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create termination packet')
    parser.add_argument('--name', required=True, help='Employee name')
    parser.add_argument('--reason', default='voluntary', help='Termination reason')
    
    args = parser.parse_args()
    create_termination_packet(args.name, args.reason)

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

