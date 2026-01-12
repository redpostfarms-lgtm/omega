# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# TRADEMARK NOTICE: "Omega" and "Ω" are trademarks of Red Post Farms, LLC.
#
"""
Voice Intent Recognition System
Classifies user intent from voice commands.

Red Post Farms, LLC - 2026
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

BRAIN = Path(r'D:\RPF_BRAIN')
INTENT_MODEL_DIR = BRAIN / 'Archived' / 'voice_intents'
INTENT_MODEL_DIR.mkdir(parents=True, exist_ok=True)

class IntentRecognizer:
    def __init__(self):
        self.intents = {
            'search': ['search', 'find', 'look up', 'research', 'go to school', 'go to college'],
            'council': ['council', 'solve', 'debate', 'agent council'],
            'hive': ['hive', 'swarm', 'multiply'],
            'memory': ['remember', 'store', 'save', 'add fact'],
            'publish': ['publish brain', 'publish memory'],
            'recover': ['recover memory', 'restore memory'],
            'health': ['health', 'status', 'system health'],
            'stats': ['stats', 'statistics', 'info']
        }
        self.training_data = []
        self._load_training_data()
    
    def _load_training_data(self):
        """Load training data."""
        training_file = INTENT_MODEL_DIR / "training.json"
        if training_file.exists():
            try:
                with open(training_file, 'r', encoding='utf-8') as f:
                    self.training_data = json.load(f)
            except: pass
    
    def classify_intent(self, text: str) -> Dict:
        """Classify intent from text."""
        text_lower = text.lower()
        scores = {}
        
        for intent, keywords in self.intents.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[intent] = score
        
        if not scores:
            return {"intent": "unknown", "confidence": 0.0, "text": text}
        
        best_intent = max(scores.items(), key=lambda x: x[1])
        confidence = min(1.0, best_intent[1] / 3.0)  # Normalize confidence
        
        return {
            "intent": best_intent[0],
            "confidence": confidence,
            "text": text,
            "all_scores": scores
        }
    
    def train_intent_model(self, text: str, intent: str):
        """Train intent model with example."""
        self.training_data.append({"text": text, "intent": intent})
        training_file = INTENT_MODEL_DIR / "training.json"
        with open(training_file, 'w', encoding='utf-8') as f:
            json.dump(self.training_data[-1000:], f, indent=2)
        
        # Update intent keywords based on training
        if intent not in self.intents:
            self.intents[intent] = []
        words = text.lower().split()
        for word in words:
            if len(word) > 3 and word not in self.intents[intent]:
                self.intents[intent].append(word)

def main():
    recognizer = IntentRecognizer()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python voice_intent.py <text> [train <intent>]")
        return
    text = sys.argv[1]
    if len(sys.argv) > 3 and sys.argv[2] == "train":
        recognizer.train_intent_model(text, sys.argv[3])
        print(f"OK Trained: '{text}' -> {sys.argv[3]}")
    else:
        result = recognizer.classify_intent(text)
        print(f"Intent: {result['intent']} (confidence: {result['confidence']:.2f})")

if __name__ == "__main__":
    main()

