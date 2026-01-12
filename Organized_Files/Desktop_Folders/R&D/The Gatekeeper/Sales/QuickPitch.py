#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# QUICKPITCH v1 - FAST MODE – NO DELAY, INSTANT PITCHES
# Zero sleep, zero wait. Pure speed. No voice. No loops. No delay.

# Mute voice, get text only
def fast_pitch(item):
    """Re-use the original logic but mute audio, return text instantly."""
    item_lower = item.lower()
    
    # Hardcoded fast pitches - no file I/O, no TTS, no imports
    if 'beef' in item_lower or 'steak' in item_lower:
        text = "Grass-fed, dry-aged twenty-eight days. One bite and you'll forget grocery store meat."
    elif 'egg' in item_lower:
        text = "Pasture-raised, blue yolks, shell so strong you can crack walnuts."
    elif 'casting' in item_lower or 'worm' in item_lower:
        text = "Night-crawler rocket fuel. One pound turns four square feet of dirt into black gold."
    elif 'tomato' in item_lower:
        text = "Sun-ripened at nine A.M., on your plate at eleven. Fresher than your neighbor's fridge."
    else:
        text = f"Farm-fresh {item}. Local. Organic. Zero miles. Tastes like it should."
    
    print(f"[{item.upper()}] {text}")
    return text

# Blast all four
if __name__ == '__main__':
    fast_pitch('beef')
    fast_pitch('eggs')
    fast_pitch('castings')
    fast_pitch('tomatoes')

