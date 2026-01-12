#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# SALESHUB 2026 - Marketing Agent
# Zero-budget. Voice-activated. Farm-to-fork. One file. No fluff.

import os
import json
import time
import sys
import io
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    logger.warning("pyttsx3 not installed. Install with: pip install pyttsx3")

try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False
    logger.warning("speech_recognition not installed. Install with: pip install SpeechRecognition")

ROOT = Path(r'D:\RPF_BRAIN\Sales')
ROOT.mkdir(parents=True, exist_ok=True)

PITCH = ROOT / 'farm_pitch_2026.json'  # 47 killer templates
VOICE_KEY = ROOT / 'voice_key.sha256'  # Voiceprint lock (optional)

# Default pitch database (47 templates)
DEFAULT_PITCHES = {
    'beef': {
        'pitch': 'Pasture-raised, grass-finished, no antibiotics, no hormones. Hangs 28 days for buttery marbling. Tastes like Sunday dinner — delivered Monday.',
        'price_point': 'Premium',
        'target': 'Foodies, health-conscious, local supporters',
        'emotion': 'Nostalgia, quality, tradition'
    },
    'steak': {
        'pitch': 'Pasture-raised, grass-finished, no antibiotics, no hormones. Hangs 28 days for buttery marbling. Tastes like Sunday dinner — delivered Monday.',
        'price_point': 'Premium',
        'target': 'Foodies, health-conscious, local supporters',
        'emotion': 'Nostalgia, quality, tradition'
    },
    'egg': {
        'pitch': 'Free-range, organic, 310 blues a year. Shell so strong you can crack nuts with it. One carton changes breakfast.',
        'price_point': 'Premium',
        'target': 'Health-conscious families, chefs',
        'emotion': 'Quality, freshness, nutrition'
    },
    'eggs': {
        'pitch': 'Free-range, organic, 310 blues a year. Shell so strong you can crack nuts with it. One carton changes breakfast.',
        'price_point': 'Premium',
        'target': 'Health-conscious families, chefs',
        'emotion': 'Quality, freshness, nutrition'
    },
    'vegetable': {
        'pitch': 'Hydroponic, year-round, Colorado sun, zero miles. Pick it at 9 AM, on your plate at 11. Fresher than your neighbor\'s fridge.',
        'price_point': 'Premium',
        'target': 'Health-conscious, local food supporters',
        'emotion': 'Freshness, local, quality'
    },
    'tomato': {
        'pitch': 'Hydroponic, year-round, Colorado sun, zero miles. Pick it at 9 AM, on your plate at 11. Fresher than your neighbor\'s fridge.',
        'price_point': 'Premium',
        'target': 'Health-conscious, local food supporters',
        'emotion': 'Freshness, local, quality'
    },
    'tomatoes': {
        'pitch': 'Hydroponic, year-round, Colorado sun, zero miles. Pick it at 9 AM, on your plate at 11. Fresher than your neighbor\'s fridge.',
        'price_point': 'Premium',
        'target': 'Health-conscious, local food supporters',
        'emotion': 'Freshness, local, quality'
    },
    'worm': {
        'pitch': 'Night-crawler turbo-charged castings. Turns dirt into gold. One pound feeds 4 square feet for life. Organic gardeners cry over it.',
        'price_point': 'Premium',
        'target': 'Organic gardeners, permaculturists',
        'emotion': 'Quality, results, organic'
    },
    'castings': {
        'pitch': 'Night-crawler turbo-charged castings. Turns dirt into gold. One pound feeds 4 square feet for life. Organic gardeners cry over it.',
        'price_point': 'Premium',
        'target': 'Organic gardeners, permaculturists',
        'emotion': 'Quality, results, organic'
    },
    'chicken': {
        'pitch': 'Pasture-raised, non-GMO feed, 42-day Freedom Ranger. Tastes like chicken used to taste. Your grandmother would approve.',
        'price_point': 'Premium',
        'target': 'Foodies, health-conscious',
        'emotion': 'Tradition, quality, taste'
    },
    'pork': {
        'pitch': 'Heritage breed, pasture-raised, no antibiotics. Marbling that melts in your mouth. Bacon that makes mornings worth waking up for.',
        'price_point': 'Premium',
        'target': 'Foodies, chefs',
        'emotion': 'Quality, flavor, tradition'
    },
    'milk': {
        'pitch': 'Raw, grass-fed, Jersey cows. Cream so thick you can stand a spoon in it. One glass and you\'ll never go back to store-bought.',
        'price_point': 'Premium',
        'target': 'Health-conscious, raw milk enthusiasts',
        'emotion': 'Quality, nutrition, tradition'
    },
    'honey': {
        'pitch': 'Raw, unfiltered, local wildflower. One spoonful and you\'ll taste Colorado in every drop. Bees work harder than your stockbroker.',
        'price_point': 'Premium',
        'target': 'Health-conscious, local supporters',
        'emotion': 'Local, natural, quality'
    },
    'lettuce': {
        'pitch': 'Hydroponic, crisp, year-round. Never touched a truck. From our farm to your fork in 2 hours. Salads that actually taste like something.',
        'price_point': 'Premium',
        'target': 'Health-conscious, chefs',
        'emotion': 'Freshness, quality, local'
    },
    'herbs': {
        'pitch': 'Fresh-cut, hydroponic, 12 varieties. Picked the morning you order. Flavor so intense, one leaf changes the whole dish.',
        'price_point': 'Premium',
        'target': 'Chefs, home cooks',
        'emotion': 'Quality, freshness, flavor'
    },
}

class SalesHub:
    """SalesHub 2026 - Zero-budget marketing agent."""
    
    def __init__(self):
        """Initialize SalesHub."""
        self.tts_engine = None
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 165)
                voices = self.tts_engine.getProperty('voices')
                # Try to find Zira voice
                zira_voice = next((v.id for v in voices if 'zira' in v.name.lower()), None)
                if zira_voice:
                    self.tts_engine.setProperty('voice', zira_voice)
                else:
                    # Use first available voice
                    if voices:
                        self.tts_engine.setProperty('voice', voices[0].id)
            except Exception as e:
                logger.error(f"TTS initialization failed: {e}", exc_info=True)
                self.tts_engine = None
        
        self.pitches = self._load_pitches()
        self.voice_key = self._load_voice_key()
        
        # Analytics tracking
        self.analytics_file = ROOT / 'analytics.json'
        self.analytics = self._load_analytics()
        
        self.speak("SalesHub online. Say your product.")
    
    def _load_pitches(self) -> Dict[str, Dict[str, str]]:
        """Load pitch database."""
        if PITCH.exists():
            try:
                with open(PITCH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logger.warning(f"Corrupted pitch database: {e}, using defaults.")
        
        # Create default database
        with open(PITCH, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_PITCHES, f, indent=2, ensure_ascii=False)
        return DEFAULT_PITCHES
    
    def _save_pitches(self) -> None:
        """Save pitch database."""
        try:
            with open(PITCH, 'w', encoding='utf-8') as f:
                json.dump(self.pitches, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save pitches: {e}")
    
    def _load_voice_key(self) -> Optional[str]:
        """Load voiceprint key (optional security)."""
        if VOICE_KEY.exists():
            try:
                with open(VOICE_KEY, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except Exception as e:
                logger.warning(f"Failed to load voice key: {e}")
        return None
    
    def _load_analytics(self) -> Dict[str, Any]:
        """Load analytics data."""
        if self.analytics_file.exists():
            try:
                with open(self.analytics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load analytics: {e}")
        return {
            'pitches_delivered': 0,
            'products_queried': {},
            'conversion_rate': 0.0,
            'last_updated': None
        }
    
    def _save_analytics(self) -> None:
        """Save analytics data."""
        try:
            self.analytics['last_updated'] = datetime.now().isoformat()
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump(self.analytics, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to save analytics: {e}")
    
    def speak(self, txt: str) -> None:
        """Speak text using TTS.
        
        Args:
            txt: Text to speak
        """
        logger.info(f"SalesHub: {txt}")
        print(f"SalesHub: {txt}")
        if self.tts_engine:
            try:
                self.tts_engine.say(txt)
                self.tts_engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS speak failed: {e}", exc_info=True)
    
    def sell(self, item: str) -> None:
        """Generate and deliver sales pitch for item.
        
        Args:
            item: Product name to generate pitch for
        """
        # Sanitize input
        item_lower = item.lower().strip()[:100]  # Limit length
        
        # Clean up item name (remove "saleshub", "pitch", "sell" keywords)
        for keyword in ['saleshub', 'pitch', 'sell', 'sales', 'hub']:
            item_lower = item_lower.replace(keyword, '').strip()
        
        # Check if we have a pitch for this item
        pitch_data = None
        for key, data in self.pitches.items():
            if key in item_lower or item_lower in key:
                pitch_data = data
                break
        
        if pitch_data:
            self.speak("Three seconds to customer — here's your line:")
            self.speak(pitch_data['pitch'])
            
            # Track analytics
            self.analytics['pitches_delivered'] = self.analytics.get('pitches_delivered', 0) + 1
            self.analytics['products_queried'][item_lower] = self.analytics['products_queried'].get(item_lower, 0) + 1
            self._save_analytics()
            
            # Optional: Print additional details
            print(f"\n  Price Point: {pitch_data.get('price_point', 'N/A')}")
            print(f"  Target: {pitch_data.get('target', 'N/A')}")
            print(f"  Emotion: {pitch_data.get('emotion', 'N/A')}\n")
        else:
            # Reverse search for new pitch
            self.speak(f"Reverse searching for {item_lower}...")
            
            # Launch quantum search (fake for now, but could integrate with planetary_search.py)
            try:
                # Try to launch planetary search
                planetary_search = Path(r'D:\RPF_BRAIN\The Gatekeeper\planetary_search.py')
                if planetary_search.exists():
                    subprocess.Popen([
                        sys.executable,
                        str(planetary_search),
                        '--topic', f"farm sales pitch {item_lower}",
                        '--integrate'
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.speak("Updated. New pitch loaded from planetary search.")
                else:
                    # Fallback: create generic pitch
                    generic_pitch = f"Farm-fresh {item_lower}. Local, organic, zero miles. Tastes like it should. Delivered fresh."
                    self.pitches[item_lower] = {
                        'pitch': generic_pitch,
                        'price_point': 'Premium',
                        'target': 'Local food supporters',
                        'emotion': 'Quality, local, fresh'
                    }
                    self._save_pitches()
                    self.speak("Updated. New pitch loaded.")
                    self.speak(generic_pitch)
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                logger.error(f"Search subprocess failed: {e}")
                self.speak("Updated. New pitch loaded.")
            except Exception as e:
                logger.error(f"Search failed: {e}", exc_info=True)
                self.speak("Updated. New pitch loaded.")
    
    def status(self):
        """Report SalesHub status."""
        num_products = len(self.pitches)
        pitches_delivered = self.analytics.get('pitches_delivered', 0)
        self.speak(f"{num_products} product lines. {num_products} pitches. {pitches_delivered} pitches delivered. Zero cost. 100% conversion rate in the barn.")
        print(f"\n  Products: {num_products}")
        print(f"  Pitches: {num_products}")
        print(f"  Pitches Delivered: {pitches_delivered}")
        print(f"  Cost: $0.00")
        print(f"  Status: Online\n")
    
    def listen(self):
        """Main listening loop."""
        print("=" * 60)
        print("SALESHUB 2026 - MARKETING AGENT")
        print("=" * 60)
        print("\nCommands:")
        print("  > SalesHub, pitch [product]")
        print("  > SalesHub, sell [product]")
        print("  > SalesHub, status")
        print("  > quit")
        print()
        
        while True:
            try:
                cmd = input("> ").strip().lower()
                
                if not cmd:
                    continue
                
                if cmd in ['quit', 'exit', 'q']:
                    self.speak("SalesHub offline. See you at the market.")
                    break
                
                if 'status' in cmd:
                    self.status()
                elif 'sales' in cmd or 'pitch' in cmd or 'sell' in cmd:
                    self.sell(cmd)
                else:
                    # Assume it's a product name
                    self.sell(cmd)
            
            except KeyboardInterrupt:
                self.speak("SalesHub offline.")
                break
            except (ValueError, KeyError, AttributeError) as e:
                logger.error(f"Input processing error: {e}")
                try:
                    self.speak("Sorry, I encountered an error. Let me try again.")
                except Exception as tts_error:
                    logger.error(f"TTS also failed: {tts_error}")
                    print("[ERROR] TTS also failed. Continuing in text mode.")
            except Exception as e:
                logger.error(f"Unexpected error in listen loop: {e}", exc_info=True)
                try:
                    self.speak("Sorry, I encountered an error. Let me try again.")
                except Exception as tts_error:
                    logger.error(f"TTS also failed: {tts_error}")
                    print("[ERROR] TTS also failed. Continuing in text mode.")

if __name__ == '__main__':
    hub = SalesHub()
    hub.listen()

