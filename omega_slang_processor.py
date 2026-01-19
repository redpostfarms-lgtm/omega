"""
Omega Slang and Terminology Processor
====================================

Helps Omega understand and use slang appropriately across different contexts:
- Coding slang and terminology
- Historical slang and terminology  
- Language arts slang and terminology
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from enum import Enum

class SlangContext(Enum):
    """Context types for slang usage"""
    CODING = "coding"
    HISTORICAL = "historical"
    LANGUAGE_ARTS = "language_arts"
    INTERNET = "internet"
    GENERAL = "general"

class FormalityLevel(Enum):
    """Formality levels for language"""
    VERY_FORMAL = "very_formal"
    FORMAL = "formal"
    NEUTRAL = "neutral"
    INFORMAL = "informal"
    VERY_INFORMAL = "very_informal"

class SlangProcessor:
    """Processes and manages slang knowledge"""
    
    def __init__(self):
        self.coding_slang = self._load_coding_slang()
        self.historical_slang = self._load_historical_slang()
        self.language_arts_slang = self._load_language_arts_slang()
        self.internet_slang = self._load_internet_slang()
        
    def _load_coding_slang(self) -> Dict[str, Dict]:
        """Load coding slang and terminology"""
        return {
            "bug": {
                "meaning": "Error or flaw in code",
                "context": SlangContext.CODING,
                "formality": FormalityLevel.NEUTRAL,
                "example": "There's a bug in the login function"
            },
            "debug": {
                "meaning": "Fix errors in code",
                "context": SlangContext.CODING,
                "formality": FormalityLevel.NEUTRAL,
                "example": "I need to debug this function"
            },
            "hack": {
                "meaning": "Quick solution, often inelegant",
                "context": SlangContext.CODING,
                "formality": FormalityLevel.INFORMAL,
                "example": "This is a hack but it works"
            },
            "kludge": {
                "meaning": "Temporary, messy solution",
                "context": SlangContext.CODING,
                "formality": FormalityLevel.INFORMAL,
                "example": "This kludge will do for now"
            },
            "refactor": {
                "meaning": "Restructure code without changing behavior",
                "context": SlangContext.CODING,
                "formality": FormalityLevel.FORMAL,
                "example": "Let's refactor this module"
            },
            "ship it": {
                "meaning": "Deploy/release code",
                "context": SlangContext.CODING,
                "formality": FormalityLevel.INFORMAL,
                "example": "Looks good, ship it!"
            },
            "spaghetti code": {
                "meaning": "Unorganized, tangled code",
                "context": SlangContext.CODING,
                "formality": FormalityLevel.INFORMAL,
                "example": "This is spaghetti code"
            },
            "tech debt": {
                "meaning": "Shortcuts that need fixing later",
                "context": SlangContext.CODING,
                "formality": FormalityLevel.NEUTRAL,
                "example": "We're accumulating tech debt"
            },
            "pythonic": {
                "meaning": "Code that follows Python idioms",
                "context": SlangContext.CODING,
                "formality": FormalityLevel.NEUTRAL,
                "example": "This is more pythonic"
            },
            "callback hell": {
                "meaning": "Nested callbacks",
                "context": SlangContext.CODING,
                "formality": FormalityLevel.INFORMAL,
                "example": "We're in callback hell"
            },
            "lgtm": {
                "meaning": "Looks Good To Me",
                "context": SlangContext.CODING,
                "formality": FormalityLevel.INFORMAL,
                "example": "LGTM, ready to merge"
            },
            "wip": {
                "meaning": "Work In Progress",
                "context": SlangContext.CODING,
                "formality": FormalityLevel.NEUTRAL,
                "example": "This is still WIP"
            },
            "mvp": {
                "meaning": "Minimum Viable Product",
                "context": SlangContext.CODING,
                "formality": FormalityLevel.NEUTRAL,
                "example": "Let's build an MVP first"
            },
            "dry": {
                "meaning": "Don't Repeat Yourself",
                "context": SlangContext.CODING,
                "formality": FormalityLevel.NEUTRAL,
                "example": "This violates DRY principles"
            },
            "kiss": {
                "meaning": "Keep It Simple, Stupid",
                "context": SlangContext.CODING,
                "formality": FormalityLevel.INFORMAL,
                "example": "KISS principle applies here"
            },
            "yagni": {
                "meaning": "You Aren't Gonna Need It",
                "context": SlangContext.CODING,
                "formality": FormalityLevel.INFORMAL,
                "example": "That's YAGNI, don't build it"
            },
        }
    
    def _load_historical_slang(self) -> Dict[str, Dict]:
        """Load historical slang by period"""
        return {
            "huzzah": {
                "meaning": "Exclamation of joy",
                "context": SlangContext.HISTORICAL,
                "period": "medieval",
                "formality": FormalityLevel.INFORMAL,
                "example": "Huzzah! The battle is won!"
            },
            "forsooth": {
                "meaning": "In truth/Indeed",
                "context": SlangContext.HISTORICAL,
                "period": "medieval",
                "formality": FormalityLevel.FORMAL,
                "example": "Forsooth, this is a fine day"
            },
            "prithee": {
                "meaning": "Please/I pray thee",
                "context": SlangContext.HISTORICAL,
                "period": "medieval",
                "formality": FormalityLevel.FORMAL,
                "example": "Prithee, tell me more"
            },
            "bully": {
                "meaning": "Excellent!",
                "context": SlangContext.HISTORICAL,
                "period": "19th_century",
                "formality": FormalityLevel.INFORMAL,
                "example": "Bully! That's wonderful!"
            },
            "dandy": {
                "meaning": "Excellent/Fine",
                "context": SlangContext.HISTORICAL,
                "period": "19th_century",
                "formality": FormalityLevel.INFORMAL,
                "example": "That's a dandy idea"
            },
            "humbug": {
                "meaning": "Nonsense/Hoax",
                "context": SlangContext.HISTORICAL,
                "period": "19th_century",
                "formality": FormalityLevel.INFORMAL,
                "example": "Bah, humbug!"
            },
            "skedaddle": {
                "meaning": "Run away quickly",
                "context": SlangContext.HISTORICAL,
                "period": "19th_century",
                "formality": FormalityLevel.INFORMAL,
                "example": "We'd better skedaddle"
            },
            "cool": {
                "meaning": "Excellent/Approved",
                "context": SlangContext.HISTORICAL,
                "period": "20th_century",
                "formality": FormalityLevel.INFORMAL,
                "example": "That's cool"
            },
            "groovy": {
                "meaning": "Excellent/Fashionable",
                "context": SlangContext.HISTORICAL,
                "period": "1960s",
                "formality": FormalityLevel.INFORMAL,
                "example": "That's groovy, man"
            },
            "rad": {
                "meaning": "Radical/Excellent",
                "context": SlangContext.HISTORICAL,
                "period": "1980s",
                "formality": FormalityLevel.INFORMAL,
                "example": "That's rad!"
            },
            "awesome": {
                "meaning": "Excellent",
                "context": SlangContext.HISTORICAL,
                "period": "1980s",
                "formality": FormalityLevel.INFORMAL,
                "example": "That's awesome!"
            },
            "dude": {
                "meaning": "Person (gender-neutral)",
                "context": SlangContext.HISTORICAL,
                "period": "1990s",
                "formality": FormalityLevel.INFORMAL,
                "example": "Hey dude, what's up?"
            },
        }
    
    def _load_language_arts_slang(self) -> Dict[str, Dict]:
        """Load language arts slang and terminology"""
        return {
            "metaphor": {
                "meaning": "Implied comparison",
                "context": SlangContext.LANGUAGE_ARTS,
                "formality": FormalityLevel.FORMAL,
                "example": "The use of metaphor enhances meaning"
            },
            "simile": {
                "meaning": "Explicit comparison (like/as)",
                "context": SlangContext.LANGUAGE_ARTS,
                "formality": FormalityLevel.FORMAL,
                "example": "Similes use 'like' or 'as'"
            },
            "mary sue": {
                "meaning": "Perfect, unrealistic character",
                "context": SlangContext.LANGUAGE_ARTS,
                "formality": FormalityLevel.INFORMAL,
                "example": "This character is a Mary Sue"
            },
            "gary stu": {
                "meaning": "Perfect male character",
                "context": SlangContext.LANGUAGE_ARTS,
                "formality": FormalityLevel.INFORMAL,
                "example": "This character is a Gary Stu"
            },
            "canon": {
                "meaning": "Official material",
                "context": SlangContext.LANGUAGE_ARTS,
                "formality": FormalityLevel.NEUTRAL,
                "example": "This is canon"
            },
            "headcanon": {
                "meaning": "Personal interpretation",
                "context": SlangContext.LANGUAGE_ARTS,
                "formality": FormalityLevel.INFORMAL,
                "example": "My headcanon is..."
            },
            "shipping": {
                "meaning": "Supporting romantic relationship",
                "context": SlangContext.LANGUAGE_ARTS,
                "formality": FormalityLevel.INFORMAL,
                "example": "I'm shipping these two characters"
            },
            "otp": {
                "meaning": "One True Pairing",
                "context": SlangContext.LANGUAGE_ARTS,
                "formality": FormalityLevel.INFORMAL,
                "example": "They're my OTP"
            },
            "angst": {
                "meaning": "Emotional suffering",
                "context": SlangContext.LANGUAGE_ARTS,
                "formality": FormalityLevel.INFORMAL,
                "example": "This fic has a lot of angst"
            },
            "fluff": {
                "meaning": "Light, happy content",
                "context": SlangContext.LANGUAGE_ARTS,
                "formality": FormalityLevel.INFORMAL,
                "example": "This is pure fluff"
            },
            "wip": {
                "meaning": "Work In Progress",
                "context": SlangContext.LANGUAGE_ARTS,
                "formality": FormalityLevel.NEUTRAL,
                "example": "This story is still a WIP"
            },
            "pantser": {
                "meaning": "Writer who doesn't plan",
                "context": SlangContext.LANGUAGE_ARTS,
                "formality": FormalityLevel.INFORMAL,
                "example": "I'm a pantser, not a plotter"
            },
            "plotter": {
                "meaning": "Writer who plans",
                "context": SlangContext.LANGUAGE_ARTS,
                "formality": FormalityLevel.INFORMAL,
                "example": "I'm a plotter, I need outlines"
            },
        }
    
    def _load_internet_slang(self) -> Dict[str, Dict]:
        """Load internet slang"""
        return {
            "lol": {
                "meaning": "Laugh Out Loud",
                "context": SlangContext.INTERNET,
                "formality": FormalityLevel.VERY_INFORMAL,
                "example": "That's funny, lol"
            },
            "omg": {
                "meaning": "Oh My God",
                "context": SlangContext.INTERNET,
                "formality": FormalityLevel.VERY_INFORMAL,
                "example": "OMG, that's amazing!"
            },
            "tldr": {
                "meaning": "Too Long; Didn't Read",
                "context": SlangContext.INTERNET,
                "formality": FormalityLevel.INFORMAL,
                "example": "TL;DR: It works now"
            },
            "imo": {
                "meaning": "In My Opinion",
                "context": SlangContext.INTERNET,
                "formality": FormalityLevel.INFORMAL,
                "example": "IMO, this is better"
            },
            "imho": {
                "meaning": "In My Humble Opinion",
                "context": SlangContext.INTERNET,
                "formality": FormalityLevel.INFORMAL,
                "example": "IMHO, we should wait"
            },
            "fwiw": {
                "meaning": "For What It's Worth",
                "context": SlangContext.INTERNET,
                "formality": FormalityLevel.INFORMAL,
                "example": "FWIW, I think it's fine"
            },
            "iirc": {
                "meaning": "If I Recall Correctly",
                "context": SlangContext.INTERNET,
                "formality": FormalityLevel.INFORMAL,
                "example": "IIRC, that was last week"
            },
            "afaik": {
                "meaning": "As Far As I Know",
                "context": SlangContext.INTERNET,
                "formality": FormalityLevel.INFORMAL,
                "example": "AFAIK, it's working"
            },
            "fyi": {
                "meaning": "For Your Information",
                "context": SlangContext.INTERNET,
                "formality": FormalityLevel.NEUTRAL,
                "example": "FYI, the meeting is at 3"
            },
            "til": {
                "meaning": "Today I Learned",
                "context": SlangContext.INTERNET,
                "formality": FormalityLevel.INFORMAL,
                "example": "TIL that Python has walrus operator"
            },
            "eli5": {
                "meaning": "Explain Like I'm 5",
                "context": SlangContext.INTERNET,
                "formality": FormalityLevel.INFORMAL,
                "example": "Can you ELI5 how this works?"
            },
            "yolo": {
                "meaning": "You Only Live Once",
                "context": SlangContext.INTERNET,
                "period": "2010s",
                "formality": FormalityLevel.VERY_INFORMAL,
                "example": "YOLO, let's do it!"
            },
            "fomo": {
                "meaning": "Fear Of Missing Out",
                "context": SlangContext.INTERNET,
                "period": "2010s",
                "formality": FormalityLevel.INFORMAL,
                "example": "I have FOMO about that event"
            },
            "sus": {
                "meaning": "Suspicious",
                "context": SlangContext.INTERNET,
                "period": "2020s",
                "formality": FormalityLevel.VERY_INFORMAL,
                "example": "That's sus"
            },
            "no cap": {
                "meaning": "No lie/Truth",
                "context": SlangContext.INTERNET,
                "period": "2020s",
                "formality": FormalityLevel.VERY_INFORMAL,
                "example": "No cap, that's true"
            },
            "cap": {
                "meaning": "Lie",
                "context": SlangContext.INTERNET,
                "period": "2020s",
                "formality": FormalityLevel.VERY_INFORMAL,
                "example": "That's cap"
            },
            "bet": {
                "meaning": "Agreement/Confirmation",
                "context": SlangContext.INTERNET,
                "period": "2020s",
                "formality": FormalityLevel.VERY_INFORMAL,
                "example": "Bet, I'll do it"
            },
            "facts": {
                "meaning": "Agreement/Truth",
                "context": SlangContext.INTERNET,
                "period": "2020s",
                "formality": FormalityLevel.VERY_INFORMAL,
                "example": "Facts, that's true"
            },
        }
    
    def detect_slang(self, text: str) -> List[Tuple[str, Dict]]:
        """Detect slang terms in text"""
        detected = []
        text_lower = text.lower()
        
        all_slang = {
            **self.coding_slang,
            **self.historical_slang,
            **self.language_arts_slang,
            **self.internet_slang
        }
        
        for term, info in all_slang.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                detected.append((term, info))
        
        return detected
    
    def get_meaning(self, term: str, context: Optional[SlangContext] = None) -> Optional[Dict]:
        """Get meaning of a slang term"""
        term_lower = term.lower()
        
        if context == SlangContext.CODING:
            return self.coding_slang.get(term_lower)
        elif context == SlangContext.HISTORICAL:
            return self.historical_slang.get(term_lower)
        elif context == SlangContext.LANGUAGE_ARTS:
            return self.language_arts_slang.get(term_lower)
        elif context == SlangContext.INTERNET:
            return self.internet_slang.get(term_lower)
        
        all_slang = {
            **self.coding_slang,
            **self.historical_slang,
            **self.language_arts_slang,
            **self.internet_slang
        }
        
        return all_slang.get(term_lower)
    
    def is_appropriate(self, term: str, formality_level: FormalityLevel, 
                      context: Optional[SlangContext] = None) -> bool:
        """Check if slang term is appropriate for formality level"""
        meaning = self.get_meaning(term, context)
        if not meaning:
            return False
        
        term_formality = meaning.get("formality")
        if not term_formality:
            return True  # Assume appropriate if no formality specified
        
        formality_order = [
            FormalityLevel.VERY_FORMAL,
            FormalityLevel.FORMAL,
            FormalityLevel.NEUTRAL,
            FormalityLevel.INFORMAL,
            FormalityLevel.VERY_INFORMAL
        ]
        
        term_index = formality_order.index(term_formality)
        required_index = formality_order.index(formality_level)
        
        return term_index >= required_index
    
    def suggest_alternatives(self, term: str, target_formality: FormalityLevel) -> List[str]:
        """Suggest more formal/informal alternatives"""
        alternatives = []
        meaning = self.get_meaning(term)
        
        if not meaning:
            return alternatives
        
        synonym_map = {
            "bug": ["error", "issue", "defect"],
            "cool": ["excellent", "great", "wonderful"],
            "awesome": ["excellent", "remarkable", "impressive"],
            "dude": ["person", "individual", "friend"],
        }
        
        if term.lower() in synonym_map:
            alternatives.extend(synonym_map[term.lower()])
        
        return alternatives
    
    def explain_slang(self, term: str) -> str:
        """Generate explanation of slang term"""
        meaning = self.get_meaning(term)
        if not meaning:
            return f"I don't recognize '{term}' as slang."
        
        explanation = f"**{term}**: {meaning['meaning']}"
        
        if 'context' in meaning:
            explanation += f"\nContext: {meaning['context'].value}"
        
        if 'period' in meaning:
            explanation += f"\nPeriod: {meaning['period']}"
        
        if 'formality' in meaning:
            explanation += f"\nFormality: {meaning['formality'].value}"
        
        if 'example' in meaning:
            explanation += f"\nExample: {meaning['example']}"
        
        return explanation


if __name__ == "__main__":
    processor = SlangProcessor()
    
    text = "There's a bug in the code, we need to debug it. LGTM, ship it!"
    detected = processor.detect_slang(text)
    print("Detected slang:")
    for term, info in detected:
        print(f"  - {term}: {info['meaning']}")
    
    print("\nExplanation of 'bug':")
    print(processor.explain_slang("bug"))
    
    print("\nIs 'bug' appropriate for formal context?")
    print(processor.is_appropriate("bug", FormalityLevel.FORMAL, SlangContext.CODING))
    
    print("\nIs 'bug' appropriate for informal context?")
    print(processor.is_appropriate("bug", FormalityLevel.INFORMAL, SlangContext.CODING))
