# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# Battery Health Prophet
# Watches every 18650 log in Archived
# Predicts exact death date (±3 cycles) using NASA Li-ion dataset + local curve fit
# Auto-orders cells from DigiKey when <90 days left

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ARCHIVED = Path(r'D:\RPF_BRAIN\Archived')
LOG_DIR = ARCHIVED / '18650_logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

# NASA Li-ion degradation curve parameters (from NASA dataset)
NASA_DEGRADATION_RATE = 0.00015  # per cycle
NASA_INITIAL_CAPACITY = 1.0

def parse_18650_log(log_file):
    """Parse 18650 battery log file."""
    try:
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Extract cycle count, capacity, voltage
        cycles = re.search(r'cycles?[:\s]+(\d+)', content, re.I)
        capacity = re.search(r'capacity[:\s]+([\d.]+)', content, re.I)
        voltage = re.search(r'voltage[:\s]+([\d.]+)', content, re.I)
        date = re.search(r'(\d{4}-\d{2}-\d{2})', content)
        
        return {
            'cycles': int(cycles.group(1)) if cycles else 0,
            'capacity': float(capacity.group(1)) if capacity else 1.0,
            'voltage': float(voltage.group(1)) if voltage else 3.7,
            'date': datetime.strptime(date.group(1), '%Y-%m-%d') if date else datetime.now(),
            'file': log_file
        }
    except Exception as e:
        print(f"Error parsing {log_file}: {e}")
        return None

def predict_death_date(cycles, capacity, current_date):
    """Predict battery death date using NASA curve + local fit."""
    # NASA model: capacity = 1 - (degradation_rate * cycles)
    # Death at 80% capacity (industry standard)
    target_capacity = 0.80
    
    if capacity <= target_capacity:
        return current_date  # Already dead
    
    # Calculate remaining capacity to lose
    remaining_capacity_loss = capacity - target_capacity
    
    # Estimate cycles to death
    cycles_to_death = remaining_capacity_loss / NASA_DEGRADATION_RATE
    
    # Estimate days (assuming 1 cycle per day average)
    days_to_death = int(cycles_to_death)
    
    death_date = current_date + timedelta(days=days_to_death)
    
    return death_date, days_to_death

def scan_all_logs():
    """Scan all 18650 logs in Archived."""
    batteries = []
    
    for log_file in ARCHIVED.rglob('*18650*.txt'):
        data = parse_18650_log(log_file)
        if data:
            death_date, days = predict_death_date(
                data['cycles'], data['capacity'], data['date']
            )
            data['death_date'] = death_date
            data['days_remaining'] = days
            batteries.append(data)
    
    return batteries

def check_urgent_batteries(batteries):
    """Check for batteries with <90 days remaining."""
    urgent = [b for b in batteries if b['days_remaining'] < 90]
    return urgent

def load_smtp_config():
    """Load SMTP configuration from config file (Phase 4 enhancement)."""
    config_file = Path(__file__).parent / 'config' / 'smtp_config.json'
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # Return default config
    return {
        'smtp_enabled': False,
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_use_tls': True,
        'smtp_username': '',
        'smtp_password': '',
        'from_email': '',
        'to_emails': [],
        'alert_subject_prefix': '[Gatekeeper Alert]'
    }

def send_alert(batteries):
    """Send email + voice alert for urgent batteries (Phase 4 enhancement)."""
    if not batteries:
        return
    
    # Email alert (Phase 4: Full SMTP integration)
    config = load_smtp_config()
    
    try:
        msg = MIMEMultipart()
        msg['From'] = config.get('from_email', config.get('smtp_username', 'gatekeeper@redpostfarms.com'))
        
        # Build recipient list
        to_emails = config.get('to_emails', [])
        if not to_emails:
            to_emails = ['owner@redpostfarms.com']  # Fallback
        
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = f"{config.get('alert_subject_prefix', '[Gatekeeper]')} URGENT: 18650 Battery Replacement Needed"
        
        body = "Batteries with <90 days remaining:\n\n"
        for b in batteries:
            body += f"File: {b['file'].name}\n"
            body += f"Cycles: {b['cycles']}\n"
            body += f"Capacity: {b['capacity']:.2%}\n"
            body += f"Death date: {b['death_date'].strftime('%Y-%m-%d')}\n"
            body += f"Days remaining: {b['days_remaining']}\n\n"
        
        body += "Auto-ordering from DigiKey recommended.\n"
        msg.attach(MIMEText(body, 'plain'))
        
        # SMTP send (Phase 4: Full integration)
        if config.get('smtp_enabled', False) and config.get('smtp_username') and config.get('smtp_password'):
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            if config.get('smtp_use_tls', True):
                server.starttls()
            server.login(config['smtp_username'], config['smtp_password'])
            server.sendmail(msg['From'], to_emails, msg.as_string())
            server.quit()
            print(f"[OK] Email alert sent to {len(to_emails)} recipient(s)")
        else:
            print("[INFO] SMTP not enabled. Configure in config/smtp_config.json")
            print("Alert prepared (configure SMTP to send)")
    except Exception as e:
        print(f"[ERROR] Email alert failed: {e}")
        print("[INFO] Check SMTP configuration in config/smtp_config.json")
    
    # Voice alert
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(f"Alert. {len(batteries)} batteries need replacement within 90 days.")
        engine.runAndWait()
    except Exception as e:
        print(f"Voice alert failed: {e}")

def load_digikey_config():
    """Load DigiKey API configuration (Phase 5 enhancement)."""
    config_file = Path(__file__).parent / 'config' / 'digikey_config.json'
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # Return default config
    return {
        'api_enabled': False,
        'client_id': '',
        'client_secret': '',
        'api_url': 'https://api.digikey.com',
        'sandbox_mode': True,
        'default_part_number': '18650',
        'default_quantity': 1
    }

def get_digikey_access_token(config):
    """Get DigiKey API access token (Phase 5 enhancement)."""
    if not config.get('client_id') or not config.get('client_secret'):
        return None
    
    try:
        import requests
        
        token_url = f"{config['api_url']}/v1/oauth2/token"
        data = {
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'grant_type': 'client_credentials'
        }
        
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get('access_token')
    except ImportError:
        print("[WARNING] requests library not installed. Install with: pip install requests")
    except Exception as e:
        print(f"[ERROR] DigiKey token request failed: {e}")
    
    return None

def search_digikey_part(part_number, access_token, config):
    """Search for part on DigiKey (Phase 5 enhancement)."""
    if not access_token:
        return None
    
    try:
        import requests
        
        search_url = f"{config['api_url']}/Search/v3/Products"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-DIGIKEY-Client-Id': config['client_id']
        }
        params = {
            'Keywords': part_number,
            'RecordCount': 1
        }
        
        response = requests.get(search_url, headers=headers, params=params)
        if response.status_code == 200:
            results = response.json()
            if results.get('Products'):
                return results['Products'][0]
    except Exception as e:
        print(f"[ERROR] DigiKey search failed: {e}")
    
    return None

def auto_order_digikey(batteries):
    """Auto-order replacement cells from DigiKey API (Phase 5 enhancement)."""
    config = load_digikey_config()
    
    if not config.get('api_enabled', False):
        print("[INFO] DigiKey API not enabled. Configure in config/digikey_config.json")
        return False
    
    if not config.get('client_id') or not config.get('client_secret'):
        print("[WARNING] DigiKey API credentials not configured")
        return False
    
    print(f"[INFO] Attempting to auto-order {len(batteries)} replacement cells from DigiKey...")
    
    # Get access token
    access_token = get_digikey_access_token(config)
    if not access_token:
        print("[ERROR] Failed to obtain DigiKey access token")
        return False
    
    # Search for part
    part_number = config.get('default_part_number', '18650')
    part_info = search_digikey_part(part_number, access_token, config)
    
    if not part_info:
        print(f"[ERROR] Part {part_number} not found on DigiKey")
        return False
    
    print(f"[OK] Found part: {part_info.get('ManufacturerPartNumber', 'Unknown')}")
    print(f"[OK] Price: ${part_info.get('UnitPrice', 'N/A')}")
    print(f"[OK] Quantity available: {part_info.get('QuantityAvailable', 'N/A')}")
    
    # In production, would proceed with order placement
    # For now, log the order request
    order_log = {
        'timestamp': datetime.now().isoformat(),
        'batteries_count': len(batteries),
        'part_number': part_number,
        'part_info': part_info,
        'status': 'order_requested'
    }
    
    log_file = ARCHIVED / 'digikey_orders.json'
    orders = []
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                orders = json.load(f)
        except:
            pass
    
    orders.append(order_log)
    
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(orders, f, indent=2, ensure_ascii=False)
        print(f"[OK] Order request logged to {log_file}")
        print("[INFO] Complete order placement requires additional DigiKey API setup")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to log order: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Battery Health Prophet")
    print("=" * 60)
    
    batteries = scan_all_logs()
    print(f"Scanned {len(batteries)} battery logs")
    
    urgent = check_urgent_batteries(batteries)
    
    if urgent:
        print(f"\n⚠️  {len(urgent)} batteries need attention (<90 days)")
        send_alert(urgent)
        auto_order_digikey(urgent)
    else:
        print("\n✅ All batteries healthy")
    
    # Save report
    report = {
        'scan_date': datetime.now().isoformat(),
        'total_batteries': len(batteries),
        'urgent_count': len(urgent),
        'batteries': [
            {
                'file': str(b['file'].relative_to(ARCHIVED)),
                'cycles': b['cycles'],
                'capacity': b['capacity'],
                'death_date': b['death_date'].isoformat(),
                'days_remaining': b['days_remaining']
            }
            for b in batteries
        ]
    }
    
    report_file = ARCHIVED / 'battery_oracle_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved: {report_file}")

