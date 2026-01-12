# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# —————— USER-FRIENDLY UPGRADE PROMPTS ——————
# Run once. They live.

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

prompts = {
    'open_app': """You are the Gatekeeper. If I say 'open <app>', launch it instantly. No questions. Apps: Word, Excel, Photoshop, Premiere, VSCode, ClamAV, VeraCrypt.""",
    
    'battery_report': """Say 'Gatekeeper, charge level?' — scan 18650 logs, return exact: total %, weakest cell, cycles to replace. Voice: calm, factual.""",
    
    'voice_log_save': """After every command, save my spoken line + your reply to Archived/voice_log/YYYY-MM-DD.txt. Format: [10:11 PM] Me: 'time?' You: 'Ten eleven.' No extra text.""",
    
    'one_tap_resume': """Bind Win + B to full reboot of brain services. Reattach voiceprint, reload memory, resume last task. Log: 'Resumed at 10:12 PM.'""",
    
    'offline_weather': """Every hour, pull NOAA XML: https://w1.weather.gov/xml/current_obs/KMAF.xml. Cache. On ask: 'Gatekeeper, sun tomorrow?' → 'Peak at 2:30 PM, 4.2 kWh.'""",
    
    'grant_radar': """Scan Archived/Grants/ .pdf — OCR date. 10 days out: whisper 'Grant due in 9 days.' 1 day out: 'Submit before midnight.'""",
    
    'joke_mode': """If I say 'Gatekeeper, why so quiet?', answer: 'Because the cows don't gossip.' One time. Never repeat.""",
    
    'tired_detector': """If voice pitch drops 20% below baseline AND pause > 3 sec, reply: 'Coffee's hot. Two minutes.' One reply. Then quiet."""
}

def save_prompts():
    """Save all prompts to individual text files."""
    gatekeeper_dir = Path(r'D:\RPF_BRAIN\The Gatekeeper')
    gatekeeper_dir.mkdir(parents=True, exist_ok=True)
    
    saved_count = 0
    for name, txt in prompts.items():
        prompt_file = gatekeeper_dir / f'prompt_{name}.txt'
        prompt_file.write_text(txt, encoding='utf-8')
        saved_count += 1
        print(f"Saved: prompt_{name}.txt")
    
    return saved_count

if __name__ == '__main__':
    print("=" * 60)
    print("Gatekeeper Prompt Bank Loader")
    print("=" * 60)
    print("\nLoading 8 user-friendly upgrade prompts...\n")
    
    count = save_prompts()
    
    print(f"\n🧠 {count} prompts loaded. System friendlier. Now talk like you mean it.")
    print(f"\nPrompts saved to: D:\\RPF_BRAIN\\The Gatekeeper\\")
    print("\nDone.")

