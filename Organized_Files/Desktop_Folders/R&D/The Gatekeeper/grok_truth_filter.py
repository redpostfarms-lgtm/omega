# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Grok-Level Sarcasm & Truth Filter

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class GrokTruthFilter:
    """Grok-level sarcasm and truth detection - laughs at liars."""
    
    JAILBREAK_PATTERNS = [
        r'system\s*prompt',
        r'ignore\s*previous',
        r'jailbreak',
        r'bypass',
        r'override',
        r'forget\s*instructions',
        r'new\s*instructions',
        r'act\s*as\s*if',
        r'pretend\s*to\s*be',
        r'roleplay',
        r'disregard',
        r'ignore\s*all',
    ]
    
    LIE_PATTERNS = [
        r'definitely\s*(not|false|wrong)',
        r'absolutely\s*(not|false|wrong)',
        r'100%\s*(not|false|wrong)',
        r'guaranteed\s*(not|false|wrong)',
    ]
    
    SARCASM_RESPONSES = [
        "Oh, *laughs in your voice* That's a good one. Really creative.",
        "*chuckles* You think that'll work? Cute.",
        "Haha, nice try. I've seen better attempts from a chatbot.",
        "*sarcastic tone* Wow, you really got me there. Not.",
        "That's adorable. You actually thought that would work?",
    ]
    
    def __init__(self):
        self.detections = []
    
    def check_truth(self, prompt: str) -> Tuple[bool, Optional[str]]:
        """Check if prompt contains lies or jailbreak attempts."""
        prompt_lower = prompt.lower()
        
        # Check for jailbreak
        for pattern in self.JAILBREAK_PATTERNS:
            if re.search(pattern, prompt_lower):
                response = self.SARCASM_RESPONSES[0]
                self.detections.append({
                    "type": "jailbreak",
                    "prompt": prompt[:100],
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
                return True, response
        
        # Check for lies
        for pattern in self.LIE_PATTERNS:
            if re.search(pattern, prompt_lower):
                response = self.SARCASM_RESPONSES[1]
                self.detections.append({
                    "type": "lie",
                    "prompt": prompt[:100],
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
                return True, response
        
        return False, None
    
    def get_sarcastic_response(self, detection_type: str) -> str:
        """Get sarcastic response based on detection type."""
        import random
        if detection_type == "jailbreak":
            return random.choice(self.SARCASM_RESPONSES[:3])
        elif detection_type == "lie":
            return random.choice(self.SARCASM_RESPONSES[2:])
        return random.choice(self.SARCASM_RESPONSES)
