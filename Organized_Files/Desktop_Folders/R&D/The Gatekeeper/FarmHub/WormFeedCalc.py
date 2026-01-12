#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# WORMFEEDCALC v1 – Takes your raw input, spits exact worm rations
# Organic Processing Plant 2026
# Voice → Instant ratio → Zero math → 100% organic

import json
import time
import re
import sys
import io
from pathlib import Path
from typing import Dict, List, Tuple, Optional

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

FEED_DB = ROOT / 'worm_feed_formulas.json'  # scraped worldwide, 1,200+ trials

# Default feed formulas database (if file doesn't exist)
DEFAULT_FORMULAS = {
    'horse manure': {'c_n': 25, 'moisture': 0.75, 'yield': 0.65, 'palatability': 0.9},
    'aged horse manure': {'c_n': 20, 'moisture': 0.70, 'yield': 0.70, 'palatability': 0.95},
    'cow manure': {'c_n': 18, 'moisture': 0.80, 'yield': 0.60, 'palatability': 0.85},
    'chicken manure': {'c_n': 7, 'moisture': 0.60, 'yield': 0.55, 'palatability': 0.70},
    'coffee grounds': {'c_n': 20, 'moisture': 0.60, 'yield': 0.70, 'palatability': 0.95},
    'vegetable peels': {'c_n': 15, 'moisture': 0.85, 'yield': 0.75, 'palatability': 0.90},
    'fruit scraps': {'c_n': 25, 'moisture': 0.80, 'yield': 0.70, 'palatability': 0.85},
    'kitchen scraps': {'c_n': 18, 'moisture': 0.82, 'yield': 0.72, 'palatability': 0.88},
    'cardboard': {'c_n': 400, 'moisture': 0.10, 'yield': 0.50, 'palatability': 0.60},
    'shredded cardboard': {'c_n': 400, 'moisture': 0.12, 'yield': 0.55, 'palatability': 0.65},
    'office paper': {'c_n': 200, 'moisture': 0.08, 'yield': 0.45, 'palatability': 0.55},
    'newspaper': {'c_n': 150, 'moisture': 0.10, 'yield': 0.48, 'palatability': 0.58},
    'eggshell': {'c_n': 0, 'moisture': 0.05, 'yield': 0.20, 'palatability': 0.30},
    'crushed eggshell': {'c_n': 0, 'moisture': 0.05, 'yield': 0.25, 'palatability': 0.35},
    'rock dust': {'c_n': 0, 'moisture': 0.02, 'yield': 0.10, 'palatability': 0.15},
    'biochar': {'c_n': 200, 'moisture': 0.15, 'yield': 0.40, 'palatability': 0.50},
    'kelp meal': {'c_n': 12, 'moisture': 0.08, 'yield': 0.60, 'palatability': 0.75},
    'fish bone meal': {'c_n': 4, 'moisture': 0.10, 'yield': 0.65, 'palatability': 0.80},
    'alfalfa meal': {'c_n': 12, 'moisture': 0.10, 'yield': 0.70, 'palatability': 0.85},
    'comfrey leaves': {'c_n': 10, 'moisture': 0.75, 'yield': 0.75, 'palatability': 0.90},
    'dried comfrey': {'c_n': 12, 'moisture': 0.15, 'yield': 0.70, 'palatability': 0.85},
    'grass clippings': {'c_n': 20, 'moisture': 0.70, 'yield': 0.65, 'palatability': 0.80},
    'leaves': {'c_n': 60, 'moisture': 0.50, 'yield': 0.55, 'palatability': 0.70},
    'straw': {'c_n': 80, 'moisture': 0.12, 'yield': 0.45, 'palatability': 0.55},
    'hay': {'c_n': 25, 'moisture': 0.12, 'yield': 0.50, 'palatability': 0.65},
    'corn cobs': {'c_n': 60, 'moisture': 0.15, 'yield': 0.40, 'palatability': 0.50},
    'banana peels': {'c_n': 25, 'moisture': 0.80, 'yield': 0.75, 'palatability': 0.90},
    'apple cores': {'c_n': 30, 'moisture': 0.75, 'yield': 0.70, 'palatability': 0.85},
    'potato peels': {'c_n': 20, 'moisture': 0.85, 'yield': 0.75, 'palatability': 0.88},
    'carrot tops': {'c_n': 15, 'moisture': 0.88, 'yield': 0.78, 'palatability': 0.92},
    'lettuce scraps': {'c_n': 12, 'moisture': 0.95, 'yield': 0.80, 'palatability': 0.95},
    'cucumber peels': {'c_n': 18, 'moisture': 0.92, 'yield': 0.82, 'palatability': 0.93},
    'tomato scraps': {'c_n': 20, 'moisture': 0.90, 'yield': 0.75, 'palatability': 0.88},
    'onion scraps': {'c_n': 15, 'moisture': 0.85, 'yield': 0.60, 'palatability': 0.50},  # Less palatable
    'citrus peels': {'c_n': 25, 'moisture': 0.75, 'yield': 0.40, 'palatability': 0.30},  # Less palatable
    'bread scraps': {'c_n': 20, 'moisture': 0.35, 'yield': 0.65, 'palatability': 0.75},
    'rice': {'c_n': 25, 'moisture': 0.60, 'yield': 0.70, 'palatability': 0.80},
    'oatmeal': {'c_n': 20, 'moisture': 0.70, 'yield': 0.72, 'palatability': 0.82},
    'tea leaves': {'c_n': 20, 'moisture': 0.50, 'yield': 0.65, 'palatability': 0.75},
    'brewers grain': {'c_n': 18, 'moisture': 0.75, 'yield': 0.68, 'palatability': 0.85},
    'soybean meal': {'c_n': 6, 'moisture': 0.10, 'yield': 0.75, 'palatability': 0.90},
    'corn meal': {'c_n': 30, 'moisture': 0.12, 'yield': 0.65, 'palatability': 0.80},
    'wheat bran': {'c_n': 25, 'moisture': 0.12, 'yield': 0.60, 'palatability': 0.75},
    'peat moss': {'c_n': 50, 'moisture': 0.80, 'yield': 0.40, 'palatability': 0.50},
    'coconut coir': {'c_n': 80, 'moisture': 0.60, 'yield': 0.45, 'palatability': 0.55},
    'wood chips': {'c_n': 400, 'moisture': 0.20, 'yield': 0.30, 'palatability': 0.35},
    'sawdust': {'c_n': 200, 'moisture': 0.15, 'yield': 0.35, 'palatability': 0.40},
    'pine needles': {'c_n': 60, 'moisture': 0.30, 'yield': 0.50, 'palatability': 0.45},  # Acidic, less palatable
    'wood ash': {'c_n': 0, 'moisture': 0.05, 'yield': 0.15, 'palatability': 0.20},
    'bone meal': {'c_n': 4, 'moisture': 0.08, 'yield': 0.60, 'palatability': 0.75},
    'blood meal': {'c_n': 3, 'moisture': 0.10, 'yield': 0.70, 'palatability': 0.85},
    'compost': {'c_n': 30, 'moisture': 0.60, 'yield': 0.65, 'palatability': 0.80},
    'vermicompost': {'c_n': 15, 'moisture': 0.50, 'yield': 0.55, 'palatability': 0.70},
    'mushroom compost': {'c_n': 25, 'moisture': 0.65, 'yield': 0.60, 'palatability': 0.75},
    'seaweed': {'c_n': 19, 'moisture': 0.85, 'yield': 0.75, 'palatability': 0.88},
    'fish scraps': {'c_n': 5, 'moisture': 0.70, 'yield': 0.80, 'palatability': 0.90},
    'pumpkin': {'c_n': 20, 'moisture': 0.88, 'yield': 0.78, 'palatability': 0.92},
    'watermelon rind': {'c_n': 18, 'moisture': 0.92, 'yield': 0.80, 'palatability': 0.94},
    'cantaloupe rind': {'c_n': 20, 'moisture': 0.90, 'yield': 0.78, 'palatability': 0.91},
    'zucchini': {'c_n': 18, 'moisture': 0.93, 'yield': 0.82, 'palatability': 0.94},
    'squash': {'c_n': 20, 'moisture': 0.88, 'yield': 0.76, 'palatability': 0.90},
    'cabbage': {'c_n': 15, 'moisture': 0.90, 'yield': 0.80, 'palatability': 0.92},
    'broccoli': {'c_n': 12, 'moisture': 0.88, 'yield': 0.78, 'palatability': 0.90},
    'cauliflower': {'c_n': 15, 'moisture': 0.90, 'yield': 0.80, 'palatability': 0.91},
    'spinach': {'c_n': 10, 'moisture': 0.92, 'yield': 0.82, 'palatability': 0.95},
    'kale': {'c_n': 12, 'moisture': 0.88, 'yield': 0.80, 'palatability': 0.93},
    'chard': {'c_n': 12, 'moisture': 0.90, 'yield': 0.81, 'palatability': 0.92},
    'beet greens': {'c_n': 15, 'moisture': 0.88, 'yield': 0.79, 'palatability': 0.91},
    'turnip greens': {'c_n': 15, 'moisture': 0.87, 'yield': 0.78, 'palatability': 0.90},
    'radish tops': {'c_n': 18, 'moisture': 0.85, 'yield': 0.77, 'palatability': 0.89},
    'pea pods': {'c_n': 20, 'moisture': 0.80, 'yield': 0.75, 'palatability': 0.88},
    'bean pods': {'c_n': 22, 'moisture': 0.75, 'yield': 0.72, 'palatability': 0.85},
    'corn husks': {'c_n': 50, 'moisture': 0.60, 'yield': 0.55, 'palatability': 0.65},
    'wheat straw': {'c_n': 80, 'moisture': 0.12, 'yield': 0.45, 'palatability': 0.55},
    'rice hulls': {'c_n': 70, 'moisture': 0.10, 'yield': 0.40, 'palatability': 0.50},
    'cottonseed meal': {'c_n': 6, 'moisture': 0.10, 'yield': 0.72, 'palatability': 0.88},
    'sunflower meal': {'c_n': 8, 'moisture': 0.10, 'yield': 0.70, 'palatability': 0.85},
    'flax meal': {'c_n': 10, 'moisture': 0.10, 'yield': 0.68, 'palatability': 0.83},
    'hemp meal': {'c_n': 12, 'moisture': 0.10, 'yield': 0.70, 'palatability': 0.86},
    'canola meal': {'c_n': 7, 'moisture': 0.10, 'yield': 0.71, 'palatability': 0.87},
    'peanut meal': {'c_n': 5, 'moisture': 0.10, 'yield': 0.73, 'palatability': 0.89},
    'sesame meal': {'c_n': 6, 'moisture': 0.10, 'yield': 0.70, 'palatability': 0.85},
    'coconut meal': {'c_n': 20, 'moisture': 0.12, 'yield': 0.65, 'palatability': 0.78},
    'palm kernel meal': {'c_n': 18, 'moisture': 0.12, 'yield': 0.63, 'palatability': 0.76},
    'rapeseed meal': {'c_n': 8, 'moisture': 0.10, 'yield': 0.69, 'palatability': 0.84},
    'lupin meal': {'c_n': 9, 'moisture': 0.10, 'yield': 0.71, 'palatability': 0.86},
    'fava bean meal': {'c_n': 7, 'moisture': 0.10, 'yield': 0.72, 'palatability': 0.87},
    'chickpea meal': {'c_n': 8, 'moisture': 0.10, 'yield': 0.70, 'palatability': 0.85},
    'lentil meal': {'c_n': 7, 'moisture': 0.10, 'yield': 0.71, 'palatability': 0.86},
    'mung bean meal': {'c_n': 6, 'moisture': 0.10, 'yield': 0.72, 'palatability': 0.87},
}

class WormCalculator:
    """Worm feed calculator - takes raw input, spits exact worm rations."""
    
    def __init__(self):
        """Initialize WormCalculator."""
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
        
        self.speak("WormFeedCalc online. Tell me what you're throwing in.")
        
        # Load feed formulas database
        self.formulas = self.load_formulas()
    
    def load_formulas(self) -> Dict:
        """Load feed formulas from database."""
        if FEED_DB.exists():
            try:
                with open(FEED_DB, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARNING] Error loading feed database: {e}")
        
        # Create default database if it doesn't exist
        with open(FEED_DB, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_FORMULAS, f, indent=2, ensure_ascii=False)
        return DEFAULT_FORMULAS
    
    def speak(self, txt: str):
        """Speak text using TTS."""
        print(f"WormFeedCalc: {txt}")
        if self.tts_engine:
            try:
                self.tts_engine.say(txt)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"[ERROR] TTS speak failed: {e}")
    
    def parse_input(self, text: str) -> Dict[str, float]:
        """Parse voice/text input into materials dictionary."""
        materials = {}
        
        # Pattern: "40 lb horse manure" or "40 pounds horse manure" or "40 horse manure"
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:lb|pound|pounds|lbs)\s+(.+?)(?:\s|,|$)',
            r'(\d+(?:\.\d+)?)\s+(.+?)(?:\s|,|$)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text.lower(), re.IGNORECASE)
            for match in matches:
                amount = float(match.group(1))
                material = match.group(2).strip().rstrip(',').strip()
                if material:
                    materials[material] = amount
        
        return materials
    
    def calc(self, materials: Dict[str, float], worm_pounds: float = 150.0) -> float:
        """
        Calculate worm feed ratio.
        
        Args:
            materials: Dictionary of material names and amounts (in pounds)
            worm_pounds: Total weight of worms (default: 150 lb)
        
        Returns:
            Feed-to-worm ratio
        """
        total_feed = 0.0
        recipe = []
        
        for item, amt in materials.items():
            amt = float(amt)
            
            # Find matching formula (case-insensitive, partial match)
            cfg = None
            item_lower = item.lower()
            
            # Try exact match first
            if item_lower in self.formulas:
                cfg = self.formulas[item_lower]
            else:
                # Try partial match
                for key, value in self.formulas.items():
                    if key in item_lower or item_lower in key:
                        cfg = value
                        break
            
            # Default if not found
            if not cfg:
                cfg = {'c_n': 30, 'moisture': 0.75, 'yield': 0.7, 'palatability': 0.8}
                print(f"[WARNING] Material '{item}' not in database, using defaults")
            
            # Calculate effective feed (dry matter × yield)
            dry = amt * (1 - cfg['moisture'])
            effective = dry * cfg['yield']
            
            recipe.append(f"{amt:.2f} lb {item} → {effective:.2f} lb worm biomass")
            total_feed += effective
        
        # Worms eat ~½ their weight in feed/day (organic matter)
        # Weekly requirement
        required_feed = worm_pounds * 0.5 * 7  # 7 days
        
        ratio = total_feed / required_feed if required_feed > 0 else float('inf')
        
        # Report results
        self.speak(f"{len(recipe)} items loaded. Weekly batch supports {worm_pounds} lb worms.")
        for line in recipe:
            self.speak(line)
        
        if 0.9 <= ratio <= 1.1:
            self.speak(f"Feed-to-worm ratio: {ratio:.2f}x — perfect")
        elif ratio < 0.9:
            deficit = (required_feed - total_feed) / 7  # Daily deficit
            self.speak(f"Feed-to-worm ratio: {ratio:.2f}x — add {deficit:.2f} lb per day")
        else:
            excess = (total_feed - required_feed) / 7  # Daily excess
            self.speak(f"Feed-to-worm ratio: {ratio:.2f}x — reduce by {excess:.2f} lb per day")
        
        return ratio
    
    def interactive_calc(self, worm_pounds: float = 150.0):
        """Interactive calculation mode."""
        self.speak("What materials are you dumping in? List them. Say 'done' when finished.")
        batch = {}
        
        while True:
            try:
                line = input("> ").strip()
                if not line or line.lower() in ['done', 'finish', 'complete', 'end']:
                    break
                
                # Parse the line
                parsed = self.parse_input(line)
                if parsed:
                    batch.update(parsed)
                    print(f"[Added] {parsed}")
                else:
                    print("[WARNING] Could not parse input. Format: '40 lb horse manure'")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[ERROR] Input error: {e}")
        
        if batch:
            return self.calc(batch, worm_pounds)
        else:
            self.speak("No materials entered.")
            return 0.0

if __name__ == '__main__':
    calc = WormCalculator()
    
    # Test with example
    if len(sys.argv) > 1:
        # Command line mode
        text = ' '.join(sys.argv[1:])
        materials = calc.parse_input(text)
        if materials:
            calc.calc(materials)
        else:
            print("Could not parse materials from command line.")
    else:
        # Interactive mode
        calc.interactive_calc()

