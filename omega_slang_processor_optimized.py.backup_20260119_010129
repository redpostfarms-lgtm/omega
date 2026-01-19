#!/usr/bin/env python3
"""
Omega Slang Processor - Space-Optimized Version
===============================================
Compact, efficient slang processing with minimal memory footprint.
"""

import re
from typing import Dict, List, Tuple, Optional, Set
from enum import IntEnum

# Use IntEnum for memory efficiency
class Context(IntEnum):
    CODING, HISTORICAL, LANGUAGE_ARTS, INTERNET = range(4)

class Formality(IntEnum):
    V_FORMAL, FORMAL, NEUTRAL, INFORMAL, V_INFORMAL = range(5)

# Compact data structure: (meaning, context, formality, example_idx)
# Examples stored separately to save space
_EXAMPLES = [
    "There's a bug in the login function", "I need to debug this function",
    "This is a hack but it works", "This kludge will do for now",
    "Let's refactor this module", "Looks good, ship it!",
    "This is spaghetti code", "We're accumulating tech debt",
    "This is more pythonic", "We're in callback hell",
    "LGTM, ready to merge", "This is still WIP",
    "Let's build an MVP first", "This violates DRY principles",
    "Huzzah! The battle is won!", "Forsooth, this is a fine day",
    "Prithee, tell me more", "Bully! That's wonderful!",
    "That's a dandy idea", "Bah, humbug!", "We'd better skedaddle",
    "That's cool", "That's groovy, man", "That's rad!", "That's awesome!",
    "Hey dude, what's up?", "The use of metaphor enhances meaning",
    "Similes use 'like' or 'as'", "This character is a Mary Sue",
    "This is canon", "My headcanon is...", "I'm shipping these two",
    "They're my OTP", "This fic has a lot of angst", "This is pure fluff",
    "This story is still a WIP", "I'm a pantser, not a plotter",
    "That's funny, lol", "OMG, that's amazing!", "TL;DR: It works now",
    "IMO, this is better", "FWIW, I think it's fine", "IIRC, that was last week",
    "AFAIK, it's working", "FYI, the meeting is at 3", "YOLO, let's do it!",
    "I have FOMO about that", "That's sus", "No cap, that's true",
    "That's cap", "Bet, I'll do it", "Facts, that's true"
]

# Compact slang dictionary: term -> (meaning_idx, context, formality, example_idx)
_SLANG_DB = {
    # Coding
    "bug": (0, Context.CODING, Formality.NEUTRAL, 0), "debug": (1, Context.CODING, Formality.NEUTRAL, 1),
    "hack": (2, Context.CODING, Formality.INFORMAL, 2), "kludge": (3, Context.CODING, Formality.INFORMAL, 3),
    "refactor": (4, Context.CODING, Formality.FORMAL, 4), "ship it": (5, Context.CODING, Formality.INFORMAL, 5),
    "spaghetti code": (6, Context.CODING, Formality.INFORMAL, 6), "tech debt": (7, Context.CODING, Formality.NEUTRAL, 7),
    "pythonic": (8, Context.CODING, Formality.NEUTRAL, 8), "callback hell": (9, Context.CODING, Formality.INFORMAL, 9),
    "lgtm": (10, Context.CODING, Formality.INFORMAL, 10), "wip": (11, Context.CODING, Formality.NEUTRAL, 11),
    "mvp": (12, Context.CODING, Formality.NEUTRAL, 12), "dry": (13, Context.CODING, Formality.NEUTRAL, 13),
    # Historical
    "huzzah": (14, Context.HISTORICAL, Formality.INFORMAL, 14), "forsooth": (15, Context.HISTORICAL, Formality.FORMAL, 15),
    "prithee": (16, Context.HISTORICAL, Formality.FORMAL, 16), "bully": (17, Context.HISTORICAL, Formality.INFORMAL, 17),
    "dandy": (18, Context.HISTORICAL, Formality.INFORMAL, 18), "humbug": (19, Context.HISTORICAL, Formality.INFORMAL, 19),
    "skedaddle": (20, Context.HISTORICAL, Formality.INFORMAL, 20), "cool": (21, Context.HISTORICAL, Formality.INFORMAL, 21),
    "groovy": (22, Context.HISTORICAL, Formality.INFORMAL, 22), "rad": (23, Context.HISTORICAL, Formality.INFORMAL, 23),
    "awesome": (24, Context.HISTORICAL, Formality.INFORMAL, 24), "dude": (25, Context.HISTORICAL, Formality.INFORMAL, 25),
    # Language Arts
    "metaphor": (26, Context.LANGUAGE_ARTS, Formality.FORMAL, 26), "simile": (27, Context.LANGUAGE_ARTS, Formality.FORMAL, 27),
    "mary sue": (28, Context.LANGUAGE_ARTS, Formality.INFORMAL, 28), "canon": (29, Context.LANGUAGE_ARTS, Formality.NEUTRAL, 29),
    "headcanon": (30, Context.LANGUAGE_ARTS, Formality.INFORMAL, 30), "shipping": (31, Context.LANGUAGE_ARTS, Formality.INFORMAL, 31),
    "otp": (32, Context.LANGUAGE_ARTS, Formality.INFORMAL, 32), "angst": (33, Context.LANGUAGE_ARTS, Formality.INFORMAL, 33),
    "fluff": (34, Context.LANGUAGE_ARTS, Formality.INFORMAL, 34), "pantser": (35, Context.LANGUAGE_ARTS, Formality.INFORMAL, 35),
    # Internet
    "lol": (36, Context.INTERNET, Formality.V_INFORMAL, 36), "omg": (37, Context.INTERNET, Formality.V_INFORMAL, 37),
    "tldr": (38, Context.INTERNET, Formality.INFORMAL, 38), "imo": (39, Context.INTERNET, Formality.INFORMAL, 39),
    "fwiw": (40, Context.INTERNET, Formality.INFORMAL, 40), "iirc": (41, Context.INTERNET, Formality.INFORMAL, 41),
    "afaik": (42, Context.INTERNET, Formality.INFORMAL, 42), "fyi": (43, Context.INTERNET, Formality.NEUTRAL, 43),
    "yolo": (44, Context.INTERNET, Formality.V_INFORMAL, 44), "fomo": (45, Context.INTERNET, Formality.INFORMAL, 45),
    "sus": (46, Context.INTERNET, Formality.V_INFORMAL, 46), "no cap": (47, Context.INTERNET, Formality.V_INFORMAL, 47),
    "cap": (48, Context.INTERNET, Formality.V_INFORMAL, 48), "bet": (49, Context.INTERNET, Formality.V_INFORMAL, 49),
    "facts": (50, Context.INTERNET, Formality.V_INFORMAL, 50),
}

_MEANINGS = [
    "Error or flaw in code", "Fix errors in code", "Quick solution, often inelegant",
    "Temporary, messy solution", "Restructure code without changing behavior", "Deploy/release code",
    "Unorganized, tangled code", "Shortcuts that need fixing later", "Code that follows Python idioms",
    "Nested callbacks", "Looks Good To Me", "Work In Progress", "Minimum Viable Product",
    "Don't Repeat Yourself", "Exclamation of joy", "In truth/Indeed", "Please/I pray thee",
    "Excellent!", "Excellent/Fine", "Nonsense/Hoax", "Run away quickly",
    "Excellent/Approved", "Excellent/Fashionable", "Radical/Excellent", "Excellent",
    "Person (gender-neutral)", "Implied comparison", "Explicit comparison (like/as)",
    "Perfect, unrealistic character", "Official material", "Personal interpretation",
    "Supporting romantic relationship", "One True Pairing", "Emotional suffering",
    "Light, happy content", "Writer who doesn't plan", "Laugh Out Loud",
    "Oh My God", "Too Long; Didn't Read", "In My Opinion", "For What It's Worth",
    "If I Recall Correctly", "As Far As I Know", "For Your Information",
    "You Only Live Once", "Fear Of Missing Out", "Suspicious", "No lie/Truth",
    "Lie", "Agreement/Confirmation", "Agreement/Truth"
]

class SlangProcessor:
    """Space-optimized slang processor"""
    
    def __init__(self):
        # Build reverse lookup for fast access
        self._term_cache: Dict[str, Tuple[int, Context, Formality, int]] = {}
        for term, data in _SLANG_DB.items():
            self._term_cache[term.lower()] = data
    
    def detect_slang(self, text: str) -> List[Tuple[str, Dict]]:
        """Detect slang terms in text - optimized"""
        detected = []
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        # Fast set intersection
        found_terms = words.intersection(self._term_cache.keys())
        
        for term in found_terms:
            meaning_idx, ctx, formality, ex_idx = self._term_cache[term]
            detected.append((term, {
                "meaning": _MEANINGS[meaning_idx],
                "context": ctx.name,
                "formality": formality.name,
                "example": _EXAMPLES[ex_idx] if ex_idx < len(_EXAMPLES) else ""
            }))
        
        return detected
    
    def get_meaning(self, term: str, context: Optional[Context] = None) -> Optional[Dict]:
        """Get meaning - optimized"""
        term_lower = term.lower()
        if term_lower not in self._term_cache:
            return None
        
        meaning_idx, ctx, formality, ex_idx = self._term_cache[term_lower]
        
        if context and ctx != context:
            return None
        
        return {
            "meaning": _MEANINGS[meaning_idx],
            "context": ctx.name,
            "formality": formality.name,
            "example": _EXAMPLES[ex_idx] if ex_idx < len(_EXAMPLES) else ""
        }
    
    def is_appropriate(self, term: str, formality_level: Formality, context: Optional[Context] = None) -> bool:
        """Check appropriateness - optimized"""
        term_lower = term.lower()
        if term_lower not in self._term_cache:
            return False
        
        _, ctx, term_formality, _ = self._term_cache[term_lower]
        
        if context and ctx != context:
            return False
        
        return term_formality.value >= formality_level.value
    
    def explain_slang(self, term: str) -> str:
        """Generate explanation - optimized"""
        meaning = self.get_meaning(term)
        if not meaning:
            return f"I don't recognize '{term}' as slang."
        
        return f"{term}: {meaning['meaning']} [{meaning['context']}] ({meaning['formality']})"

# Global singleton for space efficiency
_slang_processor = None

def get_slang_processor() -> SlangProcessor:
    """Get singleton slang processor"""
    global _slang_processor
    if _slang_processor is None:
        _slang_processor = SlangProcessor()
    return _slang_processor
