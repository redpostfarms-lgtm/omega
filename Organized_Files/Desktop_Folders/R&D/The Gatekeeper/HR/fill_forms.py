#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# FILL FORMS - Auto-fill HR forms

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(r'D:\RPF_BRAIN\HR')
NEW_HIRES_DIR = ROOT / 'New_Hires'

def fill_forms(name: str, wage: float, ssn: str = None):
    """Fill all new hire forms."""
    forms_dir = NEW_HIRES_DIR / name.replace(' ', '_')
    forms_dir.mkdir(parents=True, exist_ok=True)
    
    # I-9, W-4, HFWA, FAMLI forms
    # In production, would use PDF/DOCX libraries to fill actual forms
    # For now, create JSON data files
    
    forms_data = {
        'i9': {
            'employee_name': name,
            'hire_date': datetime.now().strftime('%Y-%m-%d'),
            'wage': wage,
            'ssn': ssn or 'N/A'
        },
        'w4': {
            'employee_name': name,
            'ssn': ssn or 'N/A',
            'filing_status': 'Single',
            'allowances': 0
        },
        'hfwa': {
            'employee_name': name,
            'psl_hours': 80,
            'accrual_rate': '1 hour per 30 hours worked'
        },
        'famli': {
            'employee_name': name,
            'payroll_tax': 0.009,
            'employee_contribution': wage * 0.0045
        }
    }
    
    with open(forms_dir / 'forms_data.json', 'w', encoding='utf-8') as f:
        json.dump(forms_data, f, indent=2, ensure_ascii=False)
    
    print(f"Forms filled for {name} in {forms_dir}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fill HR forms')
    parser.add_argument('--name', required=True, help='Employee name')
    parser.add_argument('--wage', type=float, required=True, help='Hourly wage')
    parser.add_argument('--ssn', help='Social Security Number')
    
    args = parser.parse_args()
    fill_forms(args.name, args.wage, args.ssn)

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

