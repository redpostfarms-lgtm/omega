#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# WORMFEEDCALC_PRO v2 – Bracket input, real-time mineral correction
# Bracket Mode 2026
# Input: [40] → auto-balances pH, magnesium, calcium, C/N — speaks exact grams to add

import json
import time
import re
import sys
import io
from pathlib import Path
from typing import Dict, List, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("[WARNING] pyttsx3 not installed. Install with: pip install pyttsx3")

ROOT = Path(r'D:\RPF_BRAIN\FarmHub')
ROOT.mkdir(parents=True, exist_ok=True)

NUT_DB = ROOT / 'worm_mineral_balance.json'  # pH, Mg, Ca, K, C/N from 1,800 organic trials
FEED_DB = ROOT / 'worm_feed_formulas.json'  # Existing feed formulas

# Default mineral balance database (if file doesn't exist)
DEFAULT_MINERALS = {
    'horse manure': {'mg': 0.25, 'ca': 0.35, 'k': 0.15, 'ph': 6.8},
    'aged horse manure': {'mg': 0.28, 'ca': 0.38, 'k': 0.16, 'ph': 7.0},
    'cow manure': {'mg': 0.22, 'ca': 0.30, 'k': 0.18, 'ph': 6.9},
    'chicken manure': {'mg': 0.18, 'ca': 0.45, 'k': 0.25, 'ph': 7.2},
    'coffee grounds': {'mg': 0.15, 'ca': 0.08, 'k': 0.20, 'ph': 6.5},
    'vegetable peels': {'mg': 0.12, 'ca': 0.10, 'k': 0.22, 'ph': 6.3},
    'fruit scraps': {'mg': 0.10, 'ca': 0.08, 'k': 0.25, 'ph': 5.8},
    'kitchen scraps': {'mg': 0.11, 'ca': 0.09, 'k': 0.23, 'ph': 6.2},
    'cardboard': {'mg': 0.05, 'ca': 0.02, 'k': 0.03, 'ph': 7.0},
    'shredded cardboard': {'mg': 0.05, 'ca': 0.02, 'k': 0.03, 'ph': 7.0},
    'office paper': {'mg': 0.03, 'ca': 0.01, 'k': 0.02, 'ph': 7.2},
    'newspaper': {'mg': 0.04, 'ca': 0.01, 'k': 0.02, 'ph': 7.1},
    'eggshell': {'mg': 0.01, 'ca': 38.0, 'k': 0.01, 'ph': 8.0},
    'crushed eggshell': {'mg': 0.01, 'ca': 38.0, 'k': 0.01, 'ph': 8.0},
    'rock dust': {'mg': 2.5, 'ca': 8.0, 'k': 1.2, 'ph': 7.5},
    'biochar': {'mg': 0.15, 'ca': 0.20, 'k': 0.10, 'ph': 8.5},
    'kelp meal': {'mg': 1.2, 'ca': 0.8, 'k': 2.5, 'ph': 7.0},
    'fish bone meal': {'mg': 0.5, 'ca': 22.0, 'k': 0.3, 'ph': 7.2},
    'alfalfa meal': {'mg': 0.25, 'ca': 1.2, 'k': 1.8, 'ph': 6.8},
    'comfrey leaves': {'mg': 0.30, 'ca': 1.5, 'k': 2.0, 'ph': 6.9},
    'dried comfrey': {'mg': 0.32, 'ca': 1.6, 'k': 2.1, 'ph': 7.0},
    'grass clippings': {'mg': 0.20, 'ca': 0.25, 'k': 1.5, 'ph': 6.5},
    'leaves': {'mg': 0.15, 'ca': 0.30, 'k': 0.50, 'ph': 6.2},
    'straw': {'mg': 0.08, 'ca': 0.15, 'k': 0.30, 'ph': 7.0},
    'hay': {'mg': 0.18, 'ca': 0.40, 'k': 1.2, 'ph': 6.8},
    'corn cobs': {'mg': 0.10, 'ca': 0.12, 'k': 0.25, 'ph': 6.5},
    'banana peels': {'mg': 0.25, 'ca': 0.05, 'k': 0.35, 'ph': 5.5},
    'apple cores': {'mg': 0.08, 'ca': 0.06, 'k': 0.20, 'ph': 5.8},
    'potato peels': {'mg': 0.15, 'ca': 0.08, 'k': 0.30, 'ph': 6.0},
    'carrot tops': {'mg': 0.12, 'ca': 0.10, 'k': 0.28, 'ph': 6.2},
    'lettuce scraps': {'mg': 0.10, 'ca': 0.08, 'k': 0.25, 'ph': 6.0},
    'cucumber peels': {'mg': 0.08, 'ca': 0.06, 'k': 0.22, 'ph': 6.1},
    'tomato scraps': {'mg': 0.12, 'ca': 0.10, 'k': 0.28, 'ph': 6.2},
    'bread scraps': {'mg': 0.15, 'ca': 0.12, 'k': 0.18, 'ph': 6.5},
    'rice': {'mg': 0.12, 'ca': 0.08, 'k': 0.15, 'ph': 6.8},
    'oatmeal': {'mg': 0.18, 'ca': 0.10, 'k': 0.20, 'ph': 6.7},
    'tea leaves': {'mg': 0.20, 'ca': 0.15, 'k': 0.25, 'ph': 6.5},
    'brewers grain': {'mg': 0.22, 'ca': 0.18, 'k': 0.30, 'ph': 6.6},
    'soybean meal': {'mg': 0.28, 'ca': 0.25, 'k': 1.8, 'ph': 6.8},
    'corn meal': {'mg': 0.15, 'ca': 0.08, 'k': 0.30, 'ph': 6.5},
    'wheat bran': {'mg': 0.25, 'ca': 0.15, 'k': 0.40, 'ph': 6.7},
    'compost': {'mg': 0.20, 'ca': 0.30, 'k': 0.35, 'ph': 7.0},
    'vermicompost': {'mg': 0.22, 'ca': 0.35, 'k': 0.40, 'ph': 7.1},
    'mushroom compost': {'mg': 0.18, 'ca': 0.25, 'k': 0.30, 'ph': 6.9},
    'seaweed': {'mg': 0.35, 'ca': 0.40, 'k': 0.50, 'ph': 7.0},
    'fish scraps': {'mg': 0.15, 'ca': 0.20, 'k': 0.18, 'ph': 6.8},
    'pumpkin': {'mg': 0.12, 'ca': 0.10, 'k': 0.28, 'ph': 6.2},
    'watermelon rind': {'mg': 0.10, 'ca': 0.08, 'k': 0.25, 'ph': 6.0},
    'cantaloupe rind': {'mg': 0.11, 'ca': 0.09, 'k': 0.26, 'ph': 6.1},
    'zucchini': {'mg': 0.10, 'ca': 0.08, 'k': 0.24, 'ph': 6.0},
    'squash': {'mg': 0.12, 'ca': 0.10, 'k': 0.27, 'ph': 6.2},
    'cabbage': {'mg': 0.15, 'ca': 0.12, 'k': 0.30, 'ph': 6.3},
    'broccoli': {'mg': 0.18, 'ca': 0.15, 'k': 0.35, 'ph': 6.4},
    'cauliflower': {'mg': 0.15, 'ca': 0.12, 'k': 0.30, 'ph': 6.3},
    'spinach': {'mg': 0.25, 'ca': 0.20, 'k': 0.40, 'ph': 6.5},
    'kale': {'mg': 0.22, 'ca': 0.18, 'k': 0.38, 'ph': 6.4},
    'chard': {'mg': 0.20, 'ca': 0.15, 'k': 0.35, 'ph': 6.3},
    'beet greens': {'mg': 0.18, 'ca': 0.15, 'k': 0.32, 'ph': 6.4},
    'turnip greens': {'mg': 0.16, 'ca': 0.14, 'k': 0.30, 'ph': 6.3},
    'radish tops': {'mg': 0.14, 'ca': 0.12, 'k': 0.28, 'ph': 6.2},
    'pea pods': {'mg': 0.12, 'ca': 0.10, 'k': 0.25, 'ph': 6.3},
    'bean pods': {'mg': 0.15, 'ca': 0.12, 'k': 0.28, 'ph': 6.4},
    'corn husks': {'mg': 0.10, 'ca': 0.08, 'k': 0.20, 'ph': 6.5},
    'wheat straw': {'mg': 0.08, 'ca': 0.15, 'k': 0.30, 'ph': 7.0},
    'rice hulls': {'mg': 0.06, 'ca': 0.10, 'k': 0.18, 'ph': 6.8},
    'dolomite': {'mg': 12.0, 'ca': 22.0, 'k': 0.0, 'ph': 8.5},  # Dolomite lime
    'agricultural lime': {'mg': 0.5, 'ca': 38.0, 'k': 0.0, 'ph': 8.0},  # CaCO3
    'oyster shell': {'mg': 0.2, 'ca': 38.0, 'k': 0.0, 'ph': 8.2},  # Crushed oyster shell
    'wood ash': {'mg': 1.5, 'ca': 8.0, 'k': 3.5, 'ph': 10.0},  # High pH, high K
    'bone meal': {'mg': 0.8, 'ca': 24.0, 'k': 0.2, 'ph': 7.0},
    'blood meal': {'mg': 0.3, 'ca': 0.5, 'k': 0.8, 'ph': 6.5},  # High N
    'cottonseed meal': {'mg': 0.35, 'ca': 0.25, 'k': 1.2, 'ph': 6.5},  # High N
    'sunflower meal': {'mg': 0.40, 'ca': 0.30, 'k': 1.5, 'ph': 6.6},  # High N
    'soybean meal': {'mg': 0.28, 'ca': 0.25, 'k': 1.8, 'ph': 6.8},  # High N
}

class WormFeedPro:
    """Worm Feed Calculator Pro - Bracket mode with real-time mineral correction."""
    
    def __init__(self):
        """Initialize WormFeedPro."""
        self.tts_engine = None
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 145)
                voices = self.tts_engine.getProperty('voices')
                guy_voice = next((v.id for v in voices if 'guy' in v.name.lower()), None)
                if guy_voice:
                    self.tts_engine.setProperty('voice', guy_voice)
            except Exception as e:
                print(f"[ERROR] TTS initialization failed: {e}")
                self.tts_engine = None
        
        self.speak("Pro mode on. Say bracket, like [40]. Say done when full.")
        
        # Load databases
        self.nuts = self.load_minerals()
        self.feed = self.load_feed_formulas()
        self.batch = {}  # Current batch: {item: amount_in_lb}
    
    def load_minerals(self) -> Dict:
        """Load mineral balance database."""
        if NUT_DB.exists():
            try:
                with open(NUT_DB, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARNING] Error loading mineral database: {e}")
        
        # Create default database if it doesn't exist
        with open(NUT_DB, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_MINERALS, f, indent=2, ensure_ascii=False)
        return DEFAULT_MINERALS
    
    def load_feed_formulas(self) -> Dict:
        """Load feed formulas database."""
        if FEED_DB.exists():
            try:
                with open(FEED_DB, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARNING] Error loading feed database: {e}")
        
        # Return empty dict if not found (will use defaults)
        return {}
    
    def speak(self, txt: str):
        """Speak text using TTS."""
        print(f"WormFeedPro: {txt}")
        if self.tts_engine:
            try:
                self.tts_engine.say(txt)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"[ERROR] TTS speak failed: {e}")
    
    def parse_bracket(self, line: str) -> bool:
        """
        Parse bracket input: [40] manure or [20] coffee
        
        Returns:
            True if "done", False otherwise
        """
        line = line.strip()
        
        if line.lower() in ['done', 'finish', 'complete', 'end']:
            return True
        
        if not line.startswith('['):
            self.speak("Use brackets: [40]")
            return False
        
        try:
            # Find closing bracket
            end_bracket = line.find(']')
            if end_bracket == -1:
                self.speak("Bad format. Try [20].")
                return False
            
            # Extract amount
            amount_str = line[1:end_bracket].strip()
            amount = float(amount_str)
            
            # Extract item name (everything after ])
            item = line[end_bracket + 1:].strip().lower()
            
            if not item:
                self.speak("Specify material: [40] manure")
                return False
            
            # Add to batch
            self.batch[item] = amount
            self.speak(f"{amount:.1f} lb {item} added.")
            return False
            
        except ValueError:
            self.speak("Bad format. Try [20].")
            return False
        except Exception as e:
            self.speak(f"Parse error: {e}")
            return False
    
    def balance_minerals(self):
        """Balance minerals: pH, Mg, Ca, K, C/N ratio."""
        total_mg = 0.0
        total_ca = 0.0
        total_k = 0.0
        ph_weighted = 0.0
        total_weight = 0.0
        total_carbon = 0.0
        total_nitrogen = 0.0
        
        for item, amt in self.batch.items():
            # Get feed config
            cfg = self.feed.get(item, {'moisture': 0.75, 'c_n': 25, 'ph': 6.8})
            
            # Calculate dry matter
            dry = amt * (1 - cfg.get('moisture', 0.75))
            
            # Calculate carbon and nitrogen
            # Organic matter is ~45% carbon
            carbon = dry * 0.45 / 100  # Convert to kg
            nitrogen = carbon / cfg.get('c_n', 25)
            total_carbon += carbon
            total_nitrogen += nitrogen
            
            # Get mineral content (percent of dry matter)
            nut = self.nuts.get(item, {'mg': 0.2, 'ca': 0.3, 'k': 0.15, 'ph': 6.8})
            
            # Calculate minerals (convert % to grams)
            total_mg += dry * nut.get('mg', 0.2) / 100 * 1000  # Convert to grams
            total_ca += dry * nut.get('ca', 0.3) / 100 * 1000
            total_k += dry * nut.get('k', 0.15) / 100 * 1000
            
            # Weighted pH
            ph_weighted += nut.get('ph', 6.8) * amt
            total_weight += amt
        
        # Calculate ratios
        c_n_ratio = total_carbon / (total_nitrogen + 1e-6)
        avg_ph = ph_weighted / (total_weight + 1e-6)
        
        # Report current status
        self.speak(f"Batch C/N: {c_n_ratio:.1f}, pH: {avg_ph:.2f}")
        self.speak(f"Mg: {total_mg:.0f}g, Ca: {total_ca:.0f}g, K: {total_k:.0f}g")
        
        # TARGET for 150 lb red wigglers (weekly batch ~75 lb dry matter):
        # Mg: 280g, Ca: 420g, K: 90g, pH: 7.1, C/N: 28:1
        # These are total amounts needed for the batch
        total_batch_dry = sum(amt * (1 - self.feed.get(item, {'moisture': 0.75}).get('moisture', 0.75)) 
                             for item, amt in self.batch.items())
        
        # Scale targets based on batch size (targets are for ~75 lb dry matter)
        scale_factor = total_batch_dry / 75.0 if total_batch_dry > 0 else 1.0
        target_mg = 280 * scale_factor
        target_ca = 420 * scale_factor
        target_k = 90 * scale_factor
        target_ph = 7.1
        target_cn = 28
        
        missing = {}
        
        # Check C/N ratio
        if c_n_ratio > target_cn + 2:
            # Need nitrogen source to lower C/N
            # Each lb of N source (blood meal, cottonseed meal) adds ~16:1 N
            add_n = (c_n_ratio - target_cn) / 16
            missing['nitrogen source'] = f"{add_n:.0f} lb blood meal or cottonseed meal"
        elif c_n_ratio < target_cn - 2:
            # Need carbon source to raise C/N
            add_c = (target_cn - c_n_ratio) * 0.5
            missing['carbon source'] = f"{add_c:.0f} lb cardboard or straw"
        
        # Check pH
        if avg_ph < target_ph - 0.3:
            # Need lime to raise pH
            # 1g lime raises pH ~0.05 per 100 lb batch
            ph_deficit = target_ph - avg_ph
            add_alk = ph_deficit * 20  # 20g per 0.1 pH unit
            missing['lime'] = f"{add_alk:.0f}g agricultural lime (CaCO3)"
        elif avg_ph > target_ph + 0.3:
            # Need acidifier (sulfur, peat moss)
            ph_excess = avg_ph - target_ph
            add_acid = ph_excess * 15
            missing['acidifier'] = f"{add_acid:.0f}g elemental sulfur"
        
        # Check magnesium
        if total_mg < target_mg - 20:
            add_mg = (target_mg - total_mg) / 0.12  # Dolomite is ~12% Mg
            missing['dolomite'] = f"{add_mg:.0f}g dolomite (MgCa(CO3)2)"
        
        # Check calcium
        if total_ca < target_ca - 30:
            add_ca = (target_ca - total_ca) / 0.38  # Oyster shell is ~38% Ca
            missing['oyster shell'] = f"{add_ca:.0f}g crushed oyster shell"
        
        # Check potassium
        if total_k < target_k - 10:
            add_k = (target_k - total_k) / 0.025  # Kelp meal is ~2.5% K
            missing['kelp meal'] = f"{add_k:.0f}g kelp meal"
        elif total_k > target_k + 20:
            # Too much K - reduce or add more carbon
            excess_k = total_k - target_k
            missing['warning'] = f"Potassium high: {total_k:.0f}g (target: {target_k}g). Reduce K sources."
        
        # Report recommendations
        if missing:
            self.speak("Optimizing — add:")
            for k, v in missing.items():
                if k != 'warning':
                    self.speak(v)
                else:
                    self.speak(v)
        else:
            self.speak("Batch perfect. Zero adjustment. Worms will thrive.")
    
    def run(self):
        """Main run loop."""
        self.speak("Start batching. Use [ ] brackets.")
        while True:
            try:
                line = input("> ").strip()
                if self.parse_bracket(line):
                    # User said "done"
                    if self.batch:
                        self.balance_minerals()
                    else:
                        self.speak("No materials in batch.")
                    break
            except KeyboardInterrupt:
                self.speak("Batch cancelled.")
                break
            except Exception as e:
                print(f"[ERROR] Input error: {e}")

if __name__ == '__main__':
    calc = WormFeedPro()
    calc.run()

