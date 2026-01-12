# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# TRADEMARK NOTICE: "Omega" and "Ω" are trademarks of Red Post Farms, LLC.
#
# Quick launcher for Chess AI vs AI

import sys
import subprocess
from pathlib import Path

GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')

# Create input commands
commands = "solo\n"

# Run game hub with input
try:
    process = subprocess.Popen(
        [sys.executable, str(GATE / 'game_hub_final.py')],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(GATE)
    )
    
    print("=" * 60)
    print("CHESS - AI vs AI")
    print("=" * 60)
    print("Starting solo mode...")
    print("AI will play against AI.")
    print("\nTo interact: Run 'python The Gatekeeper/game_hub_final.py' manually")
    print("Then type 'solo' to start AI vs AI mode.")
    print("=" * 60)
    
except Exception as e:
    print(f"Error: {e}")
    print("\nPlease run manually:")
    print("  python The Gatekeeper/game_hub_final.py")
    print("Then type: solo")

