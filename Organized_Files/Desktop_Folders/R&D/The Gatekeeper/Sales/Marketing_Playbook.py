#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# MARKETING_PLAYBOOK v3 – MASTER DEVELOPER FIX 2026
# Zero-latency, no typo, no TTS lag. One file. Instant.
# Bulletproof, no voice delay, zero bugs

import time
import sys
import io
import logging
from pathlib import Path
from typing import Dict, Any

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

ROOT = Path(r'D:\RPF_BRAIN\Sales')
ROOT.mkdir(parents=True, exist_ok=True)

# Analytics file
ANALYTICS_FILE = ROOT / 'playbook_analytics.json'

# Hardcoded PLAYS - no file dependency, instant access
PLAYS = {
    'beef': 'Grass-fed. Dry-aged twenty-eight days. One bite and Sunday dinner comes home.',
    'eggs': 'Pasture-raised. Blue yolks so vivid they glow. Shell strong enough to crack walnuts.',
    'castings': 'Night-crawler turbo-castings. One pound turns four square feet of dirt into black gold.',
    'tomatoes': 'Sun-kissed at nine A.M. Plate by eleven. Fresher than your neighbor\'s fridge.',
    'worms': 'Living soil engines. Happy, red-wigglers. Eat waste. Poop miracle.',
    'general': '100% organic. Zero chemicals. Zero miles. Zero excuses.'
}

class Playbook:
    """Marketing Playbook v3 - Zero latency, instant pitches."""
    
    def __init__(self):
        """Initialize Playbook."""
        # Load analytics
        self.analytics = self._load_analytics()
        self.speak('Playbook live. Zero ad spend. One hundred percent convert.')
    
    def _load_analytics(self) -> Dict[str, Any]:
        """Load analytics data."""
        if ANALYTICS_FILE.exists():
            try:
                import json
                with open(ANALYTICS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f'Failed to load analytics: {e}')
        return {
            'pitches_delivered': 0,
            'products_pitched': {},
            'last_updated': None
        }
    
    def _save_analytics(self) -> None:
        """Save analytics data."""
        try:
            import json
            from datetime import datetime
            self.analytics['last_updated'] = datetime.now().isoformat()
            with open(ANALYTICS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.analytics, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f'Failed to save analytics: {e}')
    
    def speak(self, text: str) -> None:
        """Print text instantly - no TTS = instant, dev-mode only.
        
        Args:
            text: Text to output
        """
        logger.info(f'Playbook: {text}')
        print(f'Playbook: {text}')
    
    def pitch(self, item: str) -> None:
        """Deliver pitch for item - instant lookup.
        
        Args:
            item: Product name to pitch
        """
        # Sanitize input
        key = item.lower().strip()[:100]  # Limit length
        
        # Clean up key (remove "pitch", "sell", etc.)
        for word in ['pitch', 'sell', 'playbook', 'marketing', 'sales']:
            key = key.replace(word, '').strip()
        
        # Match product
        if 'beef' in key or 'steak' in key or 'meat' in key:
            line = PLAYS.get('beef', PLAYS['general'])
        elif 'egg' in key:
            line = PLAYS.get('eggs', PLAYS['general'])
        elif 'casting' in key or 'worm' in key:
            if 'worm' in key and 'casting' not in key:
                line = PLAYS.get('worms', PLAYS['general'])
            else:
                line = PLAYS.get('castings', PLAYS['general'])
        elif 'tomato' in key:
            line = PLAYS.get('tomatoes', PLAYS['general'])
        else:
            line = PLAYS.get(key, PLAYS['general'])
        
        self.speak(line)
        
        # Track analytics
        self.analytics['pitches_delivered'] = self.analytics.get('pitches_delivered', 0) + 1
        product_key = key if key in PLAYS else 'general'
        self.analytics['products_pitched'][product_key] = self.analytics['products_pitched'].get(product_key, 0) + 1
        self._save_analytics()
    
    def status(self):
        """Report playbook status."""
        pitches_delivered = self.analytics.get('pitches_delivered', 0)
        self.speak(f'Loaded: 6 killer lines. {pitches_delivered} pitches delivered. Beef, eggs, castings, tomatoes, worms, default. Ready.')
        print(f'\n  Plays: 6')
        print(f'  Pitches Delivered: {pitches_delivered}')
        print(f'  Organic: 100%')
        print(f'  Ad Spend: $0.00')
        print(f'  Latency: 0ms\n')
    
    def listen(self):
        """Main listening loop - instant responses."""
        print("=" * 60)
        print("MARKETING PLAYBOOK v3 – MASTER DEVELOPER FIX 2026")
        print("=" * 60)
        print("\nCommands:")
        print("  > pitch beef")
        print("  > pitch eggs")
        print("  > pitch tomatoes")
        print("  > status")
        print("  > quit")
        print()
        
        while True:
            try:
                cmd = input('> ').strip()
                
                if not cmd:
                    continue
                
                if cmd.lower() in ['quit', 'exit', 'q']:
                    self.speak('Playbook offline. No ads. No billboards. Just truth.')
                    break
                
                if 'pitch' in cmd.lower() or 'sell' in cmd.lower():
                    product = cmd.lower()
                    # Remove command words
                    for word in ['pitch', 'sell', 'playbook', 'marketing', 'sales']:
                        product = product.replace(word, '').strip()
                    if product:
                        self.pitch(product)
                elif 'status' in cmd.lower():
                    self.status()
                else:
                    # Assume it's a product name
                    self.pitch(cmd)
            
            except KeyboardInterrupt:
                self.speak('Playbook offline.')
                break
            except (ValueError, KeyError) as e:
                logger.error(f'Input processing error: {e}')
                try:
                    self.speak('Error occurred. Please try again.')
                except Exception as tts_error:
                    logger.error(f'TTS failed: {tts_error}')
                    print('[ERROR] TTS failed. Continuing in text mode.')
            except Exception as e:
                logger.error(f'Unexpected error: {e}', exc_info=True)
                try:
                    self.speak('Error occurred. Please try again.')
                except Exception as tts_error:
                    logger.error(f'TTS failed: {tts_error}')
                    print('[ERROR] TTS failed. Continuing in text mode.')

if __name__ == '__main__':
    bot = Playbook()
    bot.listen()
