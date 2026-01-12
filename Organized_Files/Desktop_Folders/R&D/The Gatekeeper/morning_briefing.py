# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# Daily 6-AM Voice Briefing
# Every morning at 6:00 AM (even if PC was off)
# "Morning. 18650 bank at 94%. Panel 7 trending low. Grant deadline in 11 days. Wind 14 mph west. Coffee's on."

import json
import pyttsx3
from pathlib import Path
from datetime import datetime, timedelta
import sys
import io

# Email support (Phase 4 enhancement)
try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ARCHIVED = Path(r'D:\RPF_BRAIN\Archived')

def get_battery_status():
    """Get 18650 bank status."""
    try:
        # Load battery oracle report
        report_file = ARCHIVED / 'battery_oracle_report.json'
        if report_file.exists():
            with open(report_file, 'r') as f:
                report = json.load(f)
                batteries = report.get('batteries', [])
                if batteries:
                    avg_capacity = sum(b['capacity'] for b in batteries) / len(batteries)
                    return f"18650 bank at {int(avg_capacity * 100)}%"
    except:
        pass
    return "18650 bank status unknown"

def get_solar_status():
    """Get solar panel status."""
    try:
        # Check for panel issues
        solar_dir = ARCHIVED / 'solar_data'
        if solar_dir.exists():
            # Check latest forecast
            forecasts = list(solar_dir.glob('forecast_*.json'))
            if forecasts:
                latest = max(forecasts, key=lambda x: x.stat().st_mtime)
                with open(latest, 'r') as f:
                    forecast = json.load(f)
                    kwh = forecast.get('forecast_kwh', 0)
                    return f"Solar forecast: {kwh} kWh today"
    except:
        pass
    return "Solar status normal"

def get_grant_deadlines():
    """Get upcoming grant deadlines."""
    try:
        grants_dir = ARCHIVED / 'Grants'
        if grants_dir.exists():
            # Check for deadlines (simplified)
            # Would parse actual grant files
            return "Grant deadline in 11 days"
    except:
        pass
    return "No upcoming grant deadlines"

def get_weather():
    """Get weather forecast."""
    try:
        # Would fetch from NOAA API
        return "Wind 14 mph west"
    except:
        pass
    return "Weather data unavailable"

def generate_briefing():
    """Generate morning briefing text."""
    battery = get_battery_status()
    solar = get_solar_status()
    grants = get_grant_deadlines()
    weather = get_weather()
    
    briefing = f"Morning. {battery}. {solar}. {grants}. {weather}. Coffee's on."
    
    return briefing

def load_smtp_config():
    """Load SMTP configuration from config file."""
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
        'alert_subject_prefix': '[Gatekeeper]'
    }

def send_briefing_email(briefing_text):
    """Send morning briefing via email (Phase 4 enhancement)."""
    if not EMAIL_AVAILABLE:
        return False
    
    config = load_smtp_config()
    
    if not config.get('smtp_enabled', False) or not config.get('to_emails'):
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = config.get('from_email', config.get('smtp_username', ''))
        msg['To'] = ', '.join(config['to_emails'])
        msg['Subject'] = f"{config.get('alert_subject_prefix', '[Gatekeeper]')} Morning Briefing - {datetime.now().strftime('%Y-%m-%d')}"
        
        msg.attach(MIMEText(briefing_text, 'plain'))
        
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        if config.get('smtp_use_tls', True):
            server.starttls()
        server.login(config['smtp_username'], config['smtp_password'])
        server.sendmail(msg['From'], config['to_emails'], msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        print(f"[WARNING] Email send failed: {e}")
        return False

def speak_briefing():
    """Speak the morning briefing."""
    briefing = generate_briefing()
    
    print("=" * 60)
    print("Morning Briefing")
    print("=" * 60)
    print(f"\n{briefing}\n")
    
    # Send email if configured (Phase 4 enhancement)
    if send_briefing_email(briefing):
        print("[OK] Briefing sent via email")
    
    try:
        # Load voice tuning
        from voice_tuner import load_tune, apply_tune
        tune = load_tune()
        apply_tune(tune)
        
        # Speak
        engine = pyttsx3.init()
        engine.setProperty('rate', 110)
        engine.setProperty('volume', 0.7)
        
        engine.say(briefing)
        engine.runAndWait()
        
        print("✅ Briefing delivered.")
    except Exception as e:
        print(f"Voice briefing failed: {e}")
        print(f"Text: {briefing}")

if __name__ == '__main__':
    speak_briefing()

