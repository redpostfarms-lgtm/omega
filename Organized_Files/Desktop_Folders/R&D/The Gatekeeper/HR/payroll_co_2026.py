#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# PAYROLL CO 2026 - Colorado payroll with 2026 tables

import json
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(r'D:\RPF_BRAIN\HR')
DATA = ROOT / 'harriet_brain.json'
PAYROLL_DIR = ROOT / 'Payroll'
PAYROLL_DIR.mkdir(parents=True, exist_ok=True)

def run_payroll():
    """Run bi-weekly payroll with Colorado 2026 tables."""
    # Load employees
    if not DATA.exists():
        print("[ERROR] No employee data found")
        return
    
    with open(DATA, 'r', encoding='utf-8') as f:
        brain = json.load(f)
    
    employees = [e for e in brain.get('employees', []) if e.get('status') == 'active']
    
    payroll_date = datetime.now().strftime('%Y%m%d')
    payroll_file = PAYROLL_DIR / f'payroll_{payroll_date}.json'
    
    payroll_data = {
        'payroll_date': datetime.now().isoformat(),
        'period': 'bi-weekly',
        'employees': [],
        'totals': {
            'gross': 0,
            'net': 0,
            'taxes': 0,
            'deductions': 0
        }
    }
    
    for employee in employees:
        wage = employee.get('wage', 0)
        hours = 80  # Bi-weekly
        gross = wage * hours
        
        # Colorado 2026 deductions
        famli_employee = gross * 0.0045  # 0.45% employee share
        federal_tax = gross * 0.12  # Simplified federal
        state_tax = gross * 0.045  # Colorado simplified
        pera = gross * 0.08  # PERA (if applicable)
        
        total_deductions = famli_employee + federal_tax + state_tax + pera
        net = gross - total_deductions
        
        payroll_data['employees'].append({
            'name': employee['name'],
            'gross': round(gross, 2),
            'net': round(net, 2),
            'deductions': {
                'famli': round(famli_employee, 2),
                'federal_tax': round(federal_tax, 2),
                'state_tax': round(state_tax, 2),
                'pera': round(pera, 2)
            }
        })
        
        payroll_data['totals']['gross'] += gross
        payroll_data['totals']['net'] += net
        payroll_data['totals']['taxes'] += (federal_tax + state_tax)
        payroll_data['totals']['deductions'] += total_deductions
    
    # Round totals
    for key in payroll_data['totals']:
        payroll_data['totals'][key] = round(payroll_data['totals'][key], 2)
    
    with open(payroll_file, 'w', encoding='utf-8') as f:
        json.dump(payroll_data, f, indent=2, ensure_ascii=False)
    
    print(f"Payroll complete: {payroll_file}")
    print(f"Total gross: ${payroll_data['totals']['gross']:.2f}")
    print(f"Total net: ${payroll_data['totals']['net']:.2f}")

if __name__ == '__main__':
    run_payroll()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

